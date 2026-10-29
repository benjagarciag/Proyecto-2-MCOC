"""Visualizador térmico unificado 1D/2D/3D. Abrir no ejecuta cálculos."""
import json
import ast
import os
from pathlib import Path
import queue
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ/'desarrollo'))
os.environ.setdefault('MPLCONFIGDIR', str(RAIZ/'.venv/cache/matplotlib'))
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.animation import FFMpegWriter, PillowWriter, writers
import numpy as np
from mcplan.visualizador_termico import CASOS, predeterminados, calcular, verificar
from mcplan.barra_fuente_3d import CASOS_BARRA
from mcplan.vista_caras_3d import geometria_caras, temperaturas_caras

ENTRADAS = Path(__file__).resolve().with_name('parametros.json')
CAMPOS = [
    ('dimension', 'Dimensión (2/3 para bordes)'),
    ('Lx', 'Lx [m]'), ('Ly', 'Ly [m]'), ('Lz', 'Lz [m]'),
    ('nx', 'Nx (intervalos en 1D)'), ('ny', 'Ny'), ('nz', 'Nz'),
    ('k', 'k [W/(m K)]'), ('rho', 'rho [kg/m³]'), ('cp', 'cp [J/(kg K)]'),
    ('alpha_1d', 'alpha 1D [m²/s]'), ('tf_s', 'Tiempo final [s]'),
    ('dt_s', 'Paso dt [s] (vacío: auto)'), ('T0', 'T0 [°C]'), ('A', 'Amplitud inicial [K]'),
    ('q', 'q: fuente W/m³ / flujo W/m²'), ('h', 'h Robin [W/(m² K)]'),
    ('Tamb', 'Ambiente Robin [°C]'), ('tolerancia_K', 'Tolerancia del test [K]'),
    ('Qmax','Qmáx de la zona [W/m³]'), ('duracion_h','Duración del pulso [h]'),
    ('beta','Beta exterior [1/m]'),
    ('fuente_x','Centro de la fuente x [m]'),('fuente_y','Centro de la fuente y [m]'),('fuente_z','Centro de la fuente z [m]'),
    ('tam_x','Tamaño de fuente en x [m]'),('tam_y','Tamaño de fuente en y [m]'),('tam_z','Tamaño de fuente en z [m]'),
    ('punto_x','Observación x [m]'),('punto_y','Observación y [m]'),('punto_z','Observación z [m]'),
]
VECTORES = {
    'dimensiones':(('Lx','Ly','Lz'),'Dimensiones (x,y,z) [m]'),
    'malla':(('nx','ny','nz'),'Celdas (Nx,Ny,Nz)'),
    'centro_fuente':(('fuente_x','fuente_y','fuente_z'),'Centro de la fuente (x,y,z) [m]'),
    'tam_fuente':(('tam_x','tam_y','tam_z'),'Tamaño de la fuente (x,y,z) [m]'),
    'observacion':(('punto_x','punto_y','punto_z'),'Observación (x,y,z) [m]'),
}


def leer_vector(texto,enteros=False):
    try:
        valores=ast.literal_eval(texto.strip())
    except (ValueError,SyntaxError):
        raise ValueError('Escribe tres componentes, por ejemplo (0, 0, 0). Usa punto decimal.') from None
    if not isinstance(valores,(tuple,list)) or len(valores)!=3:
        raise ValueError('El vector debe tener exactamente tres componentes (x, y, z).')
    if any(isinstance(x,bool) or not isinstance(x,(int,float)) or not np.isfinite(x) for x in valores):
        raise ValueError('Las componentes deben ser números reales finitos.')
    if enteros and any(x!=int(x) for x in valores):
        raise ValueError('Nx, Ny y Nz deben ser enteros.')
    return tuple(int(x) if enteros else float(x) for x in valores)


def texto_vector(valores):
    return '('+', '.join(f'{x:g}' for x in valores)+')'


class Ventana:
    def __init__(self, root):
        self.root, self.vista, self.reproduciendo = root, None, False
        self._fondo, self._animados, self._reloj = None, [], None
        self.cola = queue.Queue()
        self.datos = {k: predeterminados(k) for k in CASOS}
        if ENTRADAS.exists():
            for k,datos in json.loads(ENTRADAS.read_text(encoding='utf-8')).items():
                if k in self.datos: self.datos[k].update(datos)
        root.title('Visualizador térmico · 1D / 2D / 3D')
        root.geometry('1420x940')
        panel = ttk.Frame(root, padding=10)
        panel.pack(side='left', fill='y')
        ttk.Label(panel, text='1. Elige el caso y modifica valores', font=('Segoe UI', 11, 'bold')).pack(anchor='w')
        self.nombre = tk.StringVar(value=next(iter(CASOS.values())))
        self.selector = ttk.Combobox(panel, textvariable=self.nombre, values=list(CASOS.values()), state='readonly', width=39)
        self.selector.pack(fill='x', pady=6)
        self.selector.bind('<<ComboboxSelected>>', self.cambiar_caso)
        contenedor = ttk.Frame(panel)
        contenedor.pack(fill='x')
        lienzo = tk.Canvas(contenedor,height=395,width=355,highlightthickness=0)
        desplazamiento = ttk.Scrollbar(contenedor,orient='vertical',command=lienzo.yview)
        lienzo.configure(yscrollcommand=desplazamiento.set)
        lienzo.pack(side='left',fill='x',expand=True)
        desplazamiento.pack(side='right',fill='y')
        tabla = ttk.Frame(lienzo)
        lienzo.create_window((0,0),window=tabla,anchor='nw')
        tabla.bind('<Configure>',lambda evento:lienzo.configure(scrollregion=lienzo.bbox('all')))
        self.variables = {clave:tk.StringVar() for clave,_ in CAMPOS}
        self.entradas,self.variables_vector = {},{}
        componentes={componente:grupo for grupo,(claves,_) in VECTORES.items() for componente in claves}
        campos_ui=[]
        for clave,texto in CAMPOS:
            grupo=componentes.get(clave)
            if grupo:
                if clave!=VECTORES[grupo][0][0]: continue
                campos_ui.append((grupo,VECTORES[grupo][1]))
            else: campos_ui.append((clave,texto))
        for fila, (clave, texto) in enumerate(campos_ui):
            ttk.Label(tabla, text=texto).grid(row=fila, column=0, sticky='w', pady=2)
            var = tk.StringVar() if clave in VECTORES else self.variables[clave]
            if clave in VECTORES: self.variables_vector[clave]=var
            entrada = ttk.Entry(tabla, textvariable=var, width=19)
            entrada.grid(row=fila, column=1, padx=6)
            self.entradas[clave] = entrada
        ttk.Label(tabla,text='Vectores: comas entre componentes; punto decimal.',wraplength=395).grid(row=len(campos_ui),column=0,columnspan=2,sticky='w',pady=5)
        self.descripcion = tk.StringVar()
        ttk.Label(panel, textvariable=self.descripcion, wraplength=345, justify='left').pack(fill='x', pady=8)
        self.boton = ttk.Button(panel, text='2. Ejecutar test y calcular este caso', command=self.ejecutar)
        self.boton.pack(fill='x', pady=4)
        ttk.Button(panel, text='Restaurar valores de este caso', command=self.restaurar).pack(fill='x')
        ttk.Label(panel, text='Verificación numérica y criterios térmicos:').pack(anchor='w', pady=(10, 2))
        self.resumen_estado=tk.StringVar(value='Sin ejecutar. Los límites no recortan la temperatura calculada.')
        ttk.Label(panel,textvariable=self.resumen_estado,wraplength=450).pack(anchor='w',pady=3)
        self.pestanas=ttk.Notebook(panel)
        self.pestanas.pack(fill='both',expand=True)
        self.tablas={}
        for nombre,columnas,anchos in (
            ('Resultados',('Indicador','Valor','Límite','Estado'),(145,90,65,130)),
            ('Parámetros',('Parámetro','Valor','Unidad'),(210,125,95))):
            frame=ttk.Frame(self.pestanas)
            self.pestanas.add(frame,text=nombre)
            tabla=ttk.Treeview(frame,columns=columnas,show='headings',height=9)
            for col,ancho in zip(columnas,anchos):
                tabla.heading(col,text=col); tabla.column(col,width=ancho,minwidth=45)
            scroll=ttk.Scrollbar(frame,orient='vertical',command=tabla.yview)
            tabla.configure(yscrollcommand=scroll.set)
            tabla.pack(side='left',fill='both',expand=True); scroll.pack(side='right',fill='y')
            tabla.tag_configure('error',foreground='#b00020')
            tabla.tag_configure('ok',foreground='#146b31')
            tabla.tag_configure('parcial',foreground='#805000')
            self.tablas[nombre]=tabla
        notas=ttk.Frame(self.pestanas); self.pestanas.add(notas,text='Notas')
        self.log = tk.Text(notas, width=52, height=12, wrap='word')
        self.log.pack(fill='both', expand=True)
        derecha = ttk.Frame(root)
        derecha.pack(side='right', fill='both', expand=True)
        self.fig = Figure(figsize=(9, 7), layout='constrained')
        self.canvas = FigureCanvasTkAgg(self.fig, master=derecha)
        self.canvas.mpl_connect('draw_event',self.al_dibujar)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        NavigationToolbar2Tk(self.canvas, derecha).update()
        barra = ttk.Frame(derecha, padding=8)
        barra.pack(fill='x')
        opciones = ttk.Frame(derecha,padding=(8,0))
        opciones.pack(fill='x')
        ttk.Label(opciones,text='Vista:').pack(side='left')
        self.modo_vista = tk.StringVar(value='Cortes interiores')
        vista_selector = ttk.Combobox(opciones,textvariable=self.modo_vista,
                                      values=['Cortes interiores','Volumen 3D'],state='readonly',width=19)
        vista_selector.pack(side='left',padx=5)
        vista_selector.bind('<<ComboboxSelected>>',self.cambiar_vista)
        self.modo_caras = tk.StringVar(value='Superficies físicas')
        caras_selector = ttk.Combobox(opciones,textvariable=self.modo_caras,
                                      values=['Superficies físicas','Celdas exteriores'],state='readonly',width=21)
        caras_selector.pack(side='left',padx=5)
        caras_selector.bind('<<ComboboxSelected>>',self.cambiar_vista)
        ttk.Button(opciones,text='Ver caras opuestas',command=self.girar).pack(side='left')
        ttk.Button(barra, text='▶ Reproducir', command=self.reproducir).pack(side='left')
        ttk.Button(barra, text='Pausa', command=self.pausar).pack(side='left')
        ttk.Button(barra, text='Inicio', command=lambda:self.mover(0)).pack(side='left')
        ttk.Button(barra, text='Guardar movie', command=self.exportar).pack(side='right')
        self.indice = tk.DoubleVar(value=0)
        self.slider = ttk.Scale(derecha, from_=0, to=1, variable=self.indice, command=self.actualizar)
        self.slider.bind('<ButtonPress-1>',lambda evento:self.pausar())
        self.slider.pack(fill='x', padx=12)
        self.tiempo = tk.StringVar(value='Sin cálculo: pulsa «Ejecutar test» cuando estés listo.')
        ttk.Label(derecha, textvariable=self.tiempo).pack(pady=6)
        self.cambiar_caso()
        self.fig.text(.5,.5,'Elige un caso y ejecuta su test.\nAquí verás su evolución temporal.', ha='center')
        self.canvas.draw()
        root.after(100, self.recibir)

    def clave(self):
        return next(k for k, v in CASOS.items() if v == self.nombre.get())

    def cambiar_caso(self, evento=None):
        self.pausar()
        caso = self.clave()
        for clave, variable in self.variables.items():
            variable.set('' if self.datos[caso][clave] is None else str(self.datos[caso][clave]))
        for grupo,variable in self.variables_vector.items():
            variable.set(texto_vector(self.datos[caso][k] for k in VECTORES[grupo][0]))
        activos = {'dimension','Lx','nx','tf_s','dt_s','T0','tolerancia_K'}
        dim = int(caso[-2]) if caso.startswith('seno') else self.datos[caso]['dimension']
        if dim == 1:
            activos |= {'alpha_1d','A'}
        else:
            activos |= {'Ly','ny','Lz','nz','k','rho','cp'}
            if caso.startswith('seno') or caso == 'adiabatico': activos.add('A')
            if caso in ('fuente','neumann'): activos.add('q')
            if caso == 'robin': activos |= {'h','Tamb'}
        if caso in CASOS_BARRA:
            activos = {'Lx','Ly','Lz','nx','ny','nz','k','rho','cp','tf_s','dt_s','T0','Qmax',
                       'duracion_h','fuente_x','fuente_y','fuente_z','tam_x','tam_y','tam_z',
                       'punto_x','punto_y','punto_z','tolerancia_K'}
            if caso == 'barra_beta': activos.add('beta')
        if caso.startswith('seno'): activos.discard('dimension')
        for clave, entrada in self.entradas.items():
            activo=any(k in activos for k in VECTORES[clave][0]) if clave in VECTORES else clave in activos
            entrada.configure(state='normal' if activo else 'disabled')
        textos = {
            'seno_1d':'1D: temperatura a lo largo de x. T0 fija ambos extremos; alpha se ingresa directamente. k, rho y cp no se utilizan.',
            'seno_2d':'2D: mapa XY. T0 fija las cuatro caras. El perfil inicial es T0 + A·sin(x)·sin(y), con sus longitudes.',
            'seno_3d':'3D: cortes XY, XZ e YZ. T0 fija las seis caras. El seno incluye las tres direcciones.',
            'adiabatico':'Todas las caras aisladas, sin fuente. Inicio no uniforme T0 + A·producto de cosenos. Debe conservar energía.',
            'fuente':'Inicio uniforme T0, caras aisladas y fuente constante q [W/m³]. Referencia: T0 + q·t/(rho·cp).',
            'neumann':'Flujo q [W/m²] en x mínimo; las demás caras aisladas. q positivo introduce calor. Referencia global: cambio de energía = q·área·t.',
            'robin':'Convección en x máximo; otras caras aisladas. Inicio uniforme T0. h y Tamb gobiernan el intercambio. Se verifica balance y potencia inicial.',
        }
        if caso in CASOS_BARRA:
            condicion = {'barra_d20':'Todas las caras a 20 °C.', 'barra_d30':'Todas las caras a 30 °C.',
                         'barra_n0':'Todas las caras aisladas: dT/dn=0.',
                         'barra_beta':'Normal exterior: dT/dn=beta*(T−20). beta<0 enfría; beta>0 amplifica si T>20.'}[caso]
            self.descripcion.set('Barra 3×3×6 m, z vertical, origen en el centro. '+condicion+
                                 ' Fuente en caja móvil; Q(t) cosenoidal. Desplázate en la tabla para editar fuente y observación.')
        else:
            self.descripcion.set(textos[caso]+' En 2D Lz/Nz no se usan; el espesor es 1 m.')

    def restaurar(self):
        self.datos[self.clave()] = predeterminados(self.clave())
        self.cambiar_caso()

    def ejecutar(self):
        self.pausar()
        try:
            for grupo,variable in self.variables_vector.items():
                valores=leer_vector(variable.get(),enteros=grupo=='malla')
                for clave,valor in zip(VECTORES[grupo][0],valores):
                    self.variables[clave].set(str(valor))
            c = {}
            for clave, variable in self.variables.items():
                valor = variable.get().strip().replace(',', '.')
                c[clave] = None if clave == 'dt_s' and not valor else (int(valor) if clave in ('dimension','nx','ny','nz') else float(valor))
            caso = self.clave()
            self.datos[caso] = c
            ENTRADAS.write_text(json.dumps(self.datos, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        except (ValueError, OSError) as e:
            messagebox.showerror('Revisar entradas', str(e)); return
        self.boton.configure(state='disabled')
        self.resumen_estado.set('Calculando con los parámetros indicados…')
        for tabla in self.tablas.values(): tabla.delete(*tabla.get_children())
        self.log.delete('1.0','end')
        self.log.insert('end','Calculando el caso con TUS parámetros…\n')
        def trabajo():
            try:
                v = calcular(caso, c)
                self.cola.put((v, verificar(v), None))
            except Exception as e:
                self.cola.put((None, None, str(e)))
        threading.Thread(target=trabajo, daemon=True).start()

    def recibir(self):
        try:
            v, prueba, error = self.cola.get_nowait()
            self.boton.configure(state='normal')
            if error:
                self.resumen_estado.set('No se pudo ejecutar: revisa las entradas. Detalles en Notas.')
                self.log.insert('end','NO EJECUTADO: '+error+'\n')
            else:
                self.vista = v
                ok, mensajes = prueba
                self.log.insert('end',('TEST APROBADO' if ok else 'TEST NO APROBADO')+'\n'+ '\n'.join(mensajes))
                c = v.config
                self.log.insert('end',f'\n\ndt utilizado: {v.dt:.6g} s\nLímite: {v.dt_limite:.6g} s\n'
                                     f'dx: {c["Lx"]/c["nx"]:.6g} m\nCuadros: {len(v.tiempos)}\n'
                                     'Reproducción: interpolación visual entre estados guardados.\n'
                                     'El test utiliza los campos originales, sin interpolar.\n')
                self.llenar_tablas(v,ok,mensajes)
                self.preparar_figura()
                self.slider.configure(to=len(v.tiempos)-1)
                self.mover(0)
                self.optimizar_dibujo()
        except queue.Empty:
            pass
        self.root.after(100,self.recibir)

    def llenar_tablas(self,v,ok,mensajes):
        c=v.config
        resultado=self.tablas['Resultados']; parametros=self.tablas['Parámetros']
        for tabla in self.tablas.values(): tabla.delete(*tabla.get_children())
        def fila(indicador,valor,limite='',estado='',tag=''):
            resultado.insert('', 'end',values=(indicador,valor,limite,estado),tags=(tag,) if tag else ())
        fila('Test numérico','Aprobado' if ok else 'No aprobado','', 'OK' if ok else 'Fallo','ok' if ok else 'error')
        if v.campo_exacto is not None:
            fila('Error máximo',f'{np.max(abs(v.campos-v.campo_exacto)):.6g} K',f'{c["tolerancia_K"]:g} K','Campos guardados')
        if v.energia is not None:
            fila('Residuo energía',f'{np.max(abs(v.energia-v.balance)):.4g} J','','Balance global')
        if v.potencia_esperada is not None:
            fila('Potencia inicial',f'{v.potencia_inicial:.5g} W',f'{v.potencia_esperada:.5g} W','Referencia')
        termico='Criterios térmicos no evaluados para este caso de verificación.'
        if v.extras is not None and 'criterios' in v.extras:
            m=v.extras['criterios']
            for indicador,valor,limite,cumple in (
                ('Tmax',m['Tmax_C'],70,m['cumple_Tmax']),
                ('Delta Tmax (S25)',m['DeltaTmax_K'],20,m['cumple_Delta'])):
                fila(indicador,f'{valor:.4f} °C',f'≤ {limite} °C',
                     'Dentro (estim.)' if cumple else 'EXCEDE (estim.)','ok' if cumple else 'error')
            fila('Instante de Tmax',f'{m["tiempo_Tmax_h"]:.4f} h')
            fila('Instante de Delta',f'{m["tiempo_DeltaTmax_h"]:.4f} h')
            fila('Tmin S25 en Delta',f'{m["Tmin_S25_al_Delta_C"]:.4f} °C')
            fila('Capa S25','25 mm','','Reconstrucción lineal')
            fila('Resolución S25','Primer centro ≤25 mm' if m['resuelve_s25'] else 'Primer centro >25 mm','',
                 'Requiere refinamiento' if not m['resuelve_s25'] else 'Verificar convergencia','parcial')
            fila('Horizonte',f'{m["horizonte_h"]:g} h','336 h',
                 '14 días cubiertos' if m['horizonte_14dias'] else 'PARCIAL','ok' if m['horizonte_14dias'] else 'parcial')
            termico='Límites: '+('sin superación estimada' if m['cumple_Tmax'] and m['cumple_Delta'] else 'hay superación estimada')+'.'
            self.log.insert('end','\n\nCriterios docentes: Tmax <=70 °C; Delta Tmax <=20 °C.\n'
                            'Delta T(t)=Tmax del dominio - Tmin de S25, a 25 mm de superficies.\n'
                            'Se evalúan todos los pasos numéricos, no los cuadros interpolados.\n'
                            'S25 usa reconstrucción lineal entre centros y caras, incluyendo aristas.\n'
                            'El máximo incluye centros y reconstrucción del contorno.\n'
                            'Con malla gruesa es una estimación; requiere refinamiento.\n'
                            'El proyecto requiere 14 días; 48 h es evaluación parcial.\n'
                            'No se afirma ausencia de grietas ni cumplimiento global del proyecto.\n')
        self.resumen_estado.set(('Numérico: aprobado. ' if ok else 'Numérico: no aprobado. ')+termico)
        claves={'dimension','Lx','nx','tf_s','dt_s','T0','tolerancia_K'}
        if c['dimension']==1: claves|={'alpha_1d','A'}
        else: claves|={'Ly','ny','k','rho','cp'}
        if c['dimension']==3: claves|={'Lz','nz'}
        if v.caso.startswith('seno') or v.caso=='adiabatico': claves.add('A')
        if v.caso in ('fuente','neumann'): claves.add('q')
        if v.caso=='robin': claves|={'h','Tamb'}
        if v.extras is not None:
            claves|={'Qmax','duracion_h','fuente_x','fuente_y','fuente_z','tam_x','tam_y','tam_z','punto_x','punto_y','punto_z'}
            if v.caso=='barra_beta': claves.add('beta')
        parametros.insert('','end',values=('Caso',CASOS[v.caso],''))
        agrupadas=set()
        for grupo,(componentes,texto) in VECTORES.items():
            if not any(k in claves for k in componentes): continue
            nombre,_,unidad=texto.partition('[')
            parametros.insert('','end',values=(nombre.strip(),texto_vector(c[k] for k in componentes),unidad.rstrip(']')))
            agrupadas.update(componentes)
        for clave,texto in CAMPOS:
            if clave not in claves or clave in agrupadas: continue
            nombre,_,unidad=texto.partition('[')
            valor=c[clave]
            parametros.insert('','end',values=(nombre.strip(), 'Auto' if valor is None else f'{valor:g}',unidad.rstrip(']')))
        parametros.insert('','end',values=('dt utilizado',f'{v.dt:.6g}','s'))
        parametros.insert('','end',values=('dt límite',f'{v.dt_limite:.6g}','s'))
        pasos=[c[L]/c[n] for L,n in [('Lx','nx'),('Ly','ny'),('Lz','nz')][:c['dimension']]]
        parametros.insert('','end',values=('Pasos espaciales',texto_vector(pasos),'m'))
        parametros.insert('','end',values=('Estados guardados',len(v.tiempos),''))
        self.pestanas.select(0)

    def preparar_figura(self):
        self._fondo, self._animados = None, []
        self.fig.set_layout_engine('constrained')
        self.fig.clear()
        v, c = self.vista, self.vista.config
        dim = c['dimension']
        if v.extras is not None:
            self.preparar_barra()
            return
        axs = self.fig.subplots(2,2).ravel() if dim == 3 else self.fig.subplots(1,2).ravel()
        self.dibujos = []
        minimo, maximo = float(v.campos.min()), float(v.campos.max())
        if maximo-minimo < 1e-9: maximo = minimo+1
        if dim == 1:
            self.linea, = axs[0].plot(v.coordenadas[0], v.campos[0], label='Numérica')
            self.exacta, = axs[0].plot(v.coordenadas[0], v.campo_exacto[0], '--', label='Exacta')
            axs[0].set(xlabel='x [m]', ylabel='T [°C]', ylim=(minimo-1,maximo+1), title='Perfil 1D')
            axs[0].legend()
        else:
            campos = v.campos[0]
            ix, iy = c['nx']//2, c['ny']//2
            especificaciones = [(campos if dim == 2 else campos[c['nz']//2], (0,c['Lx'],0,c['Ly']), 'x','y','Plano XY' if dim == 2 else f'Corte XY · z={v.coordenadas[2][c["nz"]//2]:.3g} m')]
            if dim == 3:
                especificaciones += [(campos[:,iy,:], (0,c['Lx'],0,c['Lz']), 'x','z',f'Corte XZ · y={v.coordenadas[1][iy]:.3g} m'),
                                     (campos[:,:,ix], (0,c['Ly'],0,c['Lz']), 'y','z',f'Corte YZ · x={v.coordenadas[0][ix]:.3g} m')]
            for ax, (campo, extent, x, y, titulo) in zip(axs, especificaciones):
                im = ax.imshow(campo, origin='lower', extent=extent, vmin=minimo, vmax=maximo, cmap='inferno', interpolation='nearest')
                self.dibujos.append(im)
                ax.set(xlabel=x+' [m]',ylabel=y+' [m]',title=titulo)
                self.fig.colorbar(im,ax=ax,label='T [°C]',shrink=.75)
        ax = axs[-1]
        planos = v.campos.reshape(len(v.tiempos),-1)
        for curva, nombre in ((planos.mean(axis=1),'Media'),(planos.max(axis=1),'Máxima'),(planos.min(axis=1),'Mínima')):
            ax.plot(v.tiempos/3600,curva,label=nombre)
        if v.media_exacta is not None:
            ax.plot(v.tiempos/3600,v.media_exacta,'k--',label='Media de referencia')
        ax.set(xlabel='Tiempo [h]',ylabel='T [°C]', title='Historia temporal')
        ax.legend(fontsize=8)
        ax.grid(alpha=.25)
        self.cursor = ax.axvline(0,color='gray',ls=':')
        self.titulo = self.fig.suptitle('')

    def preparar_barra(self):
        if self.modo_vista.get() == 'Volumen 3D':
            self.preparar_volumen()
            return
        v,c,e = self.vista,self.vista.config,self.vista.extras
        axs = self.fig.subplots(2,3).ravel()
        self.dibujos = []
        ix,iy,iz = e['indices']
        self.indices_barra = (ix,iy,iz)
        limites = [(-c[k]/2,c[k]/2) for k in ('Lx','Ly','Lz')]
        minimo,maximo = float(v.campos.min()),float(v.campos.max())
        if maximo-minimo < 1e-9: maximo = minimo+1
        campo = v.campos[0]
        especificaciones = [(campo[iz],(*limites[0],*limites[1]),'x','y',f'XY · z={v.coordenadas[2][iz]:.3g} m',(0,1)),
                             (campo[:,iy,:],(*limites[0],*limites[2]),'x','z',f'XZ · y={v.coordenadas[1][iy]:.3g} m',(0,2)),
                             (campo[:,:,ix],(*limites[1],*limites[2]),'y','z',f'YZ · x={v.coordenadas[0][ix]:.3g} m',(1,2))]
        from matplotlib.patches import Rectangle
        for ax,(imagen,extent,x,y,titulo,ejes) in zip(axs,especificaciones):
            im = ax.imshow(imagen,origin='lower',extent=extent,vmin=minimo,vmax=maximo,cmap='inferno',interpolation='nearest')
            self.dibujos.append(im)
            ax.set(xlabel=x+' [m]',ylabel=y+' [m]',title=titulo)
            i,j = ejes
            lo,hi = e['caja']
            plano_eje = ({0,1,2}-set(ejes)).pop()
            coord_corte = v.coordenadas[plano_eje][(ix,iy,iz)[plano_eje]]
            if lo[plano_eje] <= coord_corte <= hi[plano_eje]:
                ax.add_patch(Rectangle((lo[i],lo[j]),hi[i]-lo[i],hi[j]-lo[j],fill=False,edgecolor='cyan',lw=1.5))
            ax.plot(e['punto'][i],e['punto'][j],'+',color='white')
            self.fig.colorbar(im,ax=ax,label='T [°C]',shrink=.65)
        axs[3].plot(e['q_t']/3600,e['q_fuente'],label='Dentro de la fuente')
        axs[3].plot(e['q_t']/3600,e['q_punto'],'--',label='En el punto elegido')
        axs[3].set(title='Q(x,y,z,t) · fuente volumétrica',xlabel='Tiempo [h]',ylabel='Q [W/m³]')
        axs[4].plot(v.tiempos/3600,e['T_punto'],label='T en el punto (interpolada)')
        axs[4].set(title=f'Observación {tuple(float(x) for x in e["punto"])} m',xlabel='Tiempo [h]',ylabel='T [°C]')
        planos = v.campos.reshape(len(v.tiempos),-1)
        for curva,nombre in ((planos.mean(axis=1),'Media'),(planos.max(axis=1),'Máxima'),(planos.min(axis=1),'Mínima')):
            axs[5].plot(v.tiempos/3600,curva,label=nombre)
        axs[5].set(title='Historia del volumen',xlabel='Tiempo [h]',ylabel='T [°C]')
        self.cursores_barra = []
        for ax in axs[3:]:
            ax.legend(fontsize=7); ax.grid(alpha=.25)
            self.cursores_barra.append(ax.axvline(0,color='gray',ls=':'))
        self.titulo = self.fig.suptitle('')

    def preparar_volumen(self):
        from matplotlib.colors import Normalize
        from matplotlib.cm import ScalarMappable
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        v,c,e = self.vista,self.vista.config,self.vista.extras
        gs = self.fig.add_gridspec(2,3,width_ratios=[1,1,1.35])
        self.ax_volumen = self.fig.add_subplot(gs[:,:2],projection='3d')
        self.ax_volumen.set(xlim=(-c['Lx']/2,c['Lx']/2),ylim=(-c['Ly']/2,c['Ly']/2),
                            zlim=(-c['Lz']/2,c['Lz']/2),xlabel='x [m]',ylabel='y [m]',zlabel='z [m] · altura')
        self.ax_volumen.set_box_aspect((c['Lx'],c['Ly'],c['Lz']))
        self.ax_volumen.view_init(elev=22,azim=-55)
        self.ax_volumen.set_title('Arrastra con el ratón para girar el volumen',fontsize=10)
        geometria = geometria_caras(c)
        self.orden_caras = list(geometria)
        fisicas = self.modo_caras.get() == 'Superficies físicas'
        minimo,maximo = float(v.campos.min()),float(v.campos.max())
        for campo in v.campos:
            for temp in temperaturas_caras(campo,c,v.caso,fisicas).values():
                minimo,maximo = min(minimo,float(temp.min())),max(maximo,float(temp.max()))
        if maximo-minimo < 1e-9: maximo = minimo+1.
        self.norma_caras = Normalize(minimo,maximo)
        # El extremo frío azul hace legible la geometría incluso si todas
        # las superficies siguen a 20 °C; negro no equivale a ausencia de datos.
        self.mapa_caras = matplotlib.colormaps['turbo']
        self.poligonos = Poly3DCollection(np.concatenate(list(geometria.values())),
                                          linewidths=0,edgecolors='none',antialiased=False)
        self.ax_volumen.add_collection3d(self.poligonos)
        self.fig.colorbar(ScalarMappable(norm=self.norma_caras,cmap=self.mapa_caras),
                          ax=self.ax_volumen,label='Temperatura [°C] · escala fija',shrink=.6,pad=.08)
        if fisicas and v.caso in ('barra_d20','barra_d30'):
            nota='Dirichlet: las seis superficies conservan su temperatura impuesta.\nUsa «Celdas exteriores» o «Cortes interiores» para observar el interior.'
        elif fisicas:
            nota='Se colorean las seis caras físicas con la condición de borde.\nGira el volumen para observar las tres caras ocultas.'
        else:
            nota='Temperaturas de centros de celdas exteriores proyectadas sobre las caras.\nSon valores interiores próximos al contorno, no temperaturas de superficie.'
        self.ax_volumen.text2D(.5,-.06,nota,transform=self.ax_volumen.transAxes,ha='center',fontsize=8)
        self.etiqueta_caras = self.ax_volumen.text2D(.5,.98,'',transform=self.ax_volumen.transAxes,
                                                    ha='center',va='top',fontsize=9)
        self.ax_volumen.scatter(*e['punto'],color='cyan',marker='+',s=35,label='Punto interior (puede quedar oculto)')
        axq = self.fig.add_subplot(gs[0,2])
        axq.plot(e['q_t']/3600,e['q_fuente'],label='En la zona fuente')
        axq.plot(e['q_t']/3600,e['q_punto'],'--',label='En el punto elegido')
        axq.set(title='Q(t)',xlabel='Tiempo [h]',ylabel='Q [W/m³]')
        axt = self.fig.add_subplot(gs[1,2])
        planos = v.campos.reshape(len(v.tiempos),-1)
        axt.plot(v.tiempos/3600,e['T_punto'],label='Punto elegido')
        axt.plot(v.tiempos/3600,planos.max(axis=1),'--',label='Máxima del volumen')
        axt.plot(v.tiempos/3600,planos.mean(axis=1),':',label='Media del volumen')
        axt.set(title='Temperatura interior',xlabel='Tiempo [h]',ylabel='T [°C]')
        self.cursores_barra = []
        for ax in (axq,axt):
            ax.legend(fontsize=7); ax.grid(alpha=.25)
            self.cursores_barra.append(ax.axvline(0,color='gray',ls=':'))
        self.titulo = self.fig.suptitle('')

    def cambiar_vista(self,evento=None):
        if self.vista is None or self.vista.extras is None: return
        self.pausar()
        self._fondo, self._animados = None, []
        self.fig.clear()
        self.fig.set_layout_engine('constrained')
        self.preparar_barra()
        self.actualizar()
        self.optimizar_dibujo()

    def girar(self):
        if self.vista is None or self.vista.extras is None or self.modo_vista.get() != 'Volumen 3D': return
        self.ax_volumen.view_init(elev=self.ax_volumen.elev,azim=self.ax_volumen.azim+180)
        self.canvas.draw_idle()

    def actualizar(self, valor=None):
        if self.vista is None: return
        posicion = min(len(self.vista.tiempos)-1,max(0,float(self.indice.get())))
        n = int(posicion)
        siguiente = min(n+1,len(self.vista.tiempos)-1)
        fraccion = posicion-n
        v, c = self.vista, self.vista.config
        campo = v.campos[n] if fraccion == 0 else (1-fraccion)*v.campos[n]+fraccion*v.campos[siguiente]
        tiempo_s = (1-fraccion)*v.tiempos[n]+fraccion*v.tiempos[siguiente]
        if v.extras is not None:
            if self.modo_vista.get() == 'Volumen 3D':
                caras = temperaturas_caras(campo,c,v.caso,self.modo_caras.get() == 'Superficies físicas')
                valores = np.concatenate([caras[k].ravel() for k in self.orden_caras])
                self.poligonos.set_facecolor(self.mapa_caras(self.norma_caras(valores)))
                self.etiqueta_caras.set_text(f'Caras mostradas: {valores.min():.4f} a {valores.max():.4f} °C\n'
                                             f'Máxima interior: {campo.max():.4f} °C')
            else:
                ix,iy,iz = self.indices_barra
                for im,corte in zip(self.dibujos,(campo[iz],campo[:,iy,:],campo[:,:,ix])):
                    im.set_data(corte)
            for cursor in self.cursores_barra: cursor.set_xdata([tiempo_s/3600]*2)
            detalle = self.modo_caras.get() if self.modo_vista.get() == 'Volumen 3D' else 'Cortes interiores'
            self.titulo.set_text(CASOS[v.caso]+f' · t={tiempo_s/3600:.3g} h · '+detalle)
            self.tiempo.set(f't = {tiempo_s/3600:.3f} h · mín={campo.min():.4g} °C · máx={campo.max():.4g} °C · interpolación visual')
            self.dibujar_cambios()
            return
        if c['dimension'] == 1:
            exacta = (1-fraccion)*v.campo_exacto[n]+fraccion*v.campo_exacto[siguiente]
            self.linea.set_ydata(campo); self.exacta.set_ydata(exacta)
        elif c['dimension'] == 2:
            self.dibujos[0].set_data(campo)
        else:
            for im, corte in zip(self.dibujos,(campo[c['nz']//2],campo[:,c['ny']//2,:],campo[:,:,c['nx']//2])):
                im.set_data(corte)
        self.cursor.set_xdata([tiempo_s/3600]*2)
        self.titulo.set_text(CASOS[v.caso]+f' · t={tiempo_s:.3g} s ({tiempo_s/3600:.3g} h)')
        self.tiempo.set(f't = {tiempo_s/3600:.3f} h · mín={campo.min():.4g} °C · máx={campo.max():.4g} °C · interpolación visual')
        self.dibujar_cambios()

    def optimizar_dibujo(self):
        """En cortes se repintan imágenes/cursor; ejes y leyendas quedan en caché."""
        self._fondo, self._animados = None, []
        # El volumen girable necesita la proyección completa de Matplotlib.
        volumen = self.vista.extras is not None and self.modo_vista.get() == 'Volumen 3D'
        if not volumen:
            for ax in self.fig.axes:
                if ax.images:
                    self._animados += list(ax.images)+list(ax.patches)+list(ax.lines)
            if self.vista.extras is not None:
                self._animados += self.cursores_barra
            else:
                self._animados.append(self.cursor)
                if self.vista.config['dimension'] == 1:
                    self._animados += [self.linea,self.exacta]
            self._animados.append(self.titulo)
            for artista in self._animados: artista.set_animated(True)
        # No recalcular la disposición de seis paneles en cada cuadro.
        self.canvas.draw()
        self.fig.set_layout_engine(None)

    def al_dibujar(self,evento):
        if not self._animados: return
        self._fondo = self.canvas.copy_from_bbox(self.fig.bbox)
        self.dibujar_cambios()

    def dibujar_cambios(self):
        if self._animados and self._fondo is not None:
            self.canvas.restore_region(self._fondo)
            for artista in self._animados: self.fig.draw_artist(artista)
            self.canvas.blit(self.fig.bbox)
        else:
            self.canvas.draw_idle()

    def mover(self,n):
        self.indice.set(n); self.actualizar()

    def pausar(self):
        self.reproduciendo = False
        if self._reloj is not None:
            self.root.after_cancel(self._reloj)
            self._reloj = None

    def reproducir(self):
        if self.vista is None or self.reproduciendo: return
        if int(self.indice.get()) >= len(self.vista.tiempos)-1: self.mover(0)
        self.reproduciendo = True
        self._inicio_indice = float(self.indice.get())
        self._inicio_reproduccion = time.perf_counter()
        self.paso()

    def paso(self):
        self._reloj = None
        if not self.reproduciendo or self.vista is None: return
        inicio = time.perf_counter()
        ultimo = len(self.vista.tiempos)-1
        posicion = self._inicio_indice+(inicio-self._inicio_reproduccion)*ultimo/12.
        self.mover(min(posicion,ultimo))
        if posicion >= ultimo: self.pausar(); return
        demora = max(1,40-int((time.perf_counter()-inicio)*1000))
        self._reloj = self.root.after(demora,self.paso)

    def exportar(self):
        if self.vista is None:
            messagebox.showinfo('Sin simulación','Primero ejecuta el caso.'); return
        self.pausar()
        destino = RAIZ/'resultados/visualizadores'/self.vista.caso/'evolucion.mp4'
        destino.parent.mkdir(parents=True,exist_ok=True)
        writer = FFMpegWriter(fps=25,codec='libx264',extra_args=['-vf','pad=ceil(iw/2)*2:ceil(ih/2)*2','-pix_fmt','yuv420p']) if writers.is_available('ffmpeg') else PillowWriter(fps=25)
        if not writers.is_available('ffmpeg'): destino = destino.with_suffix('.gif')
        previo = float(self.indice.get())
        animados = list(self._animados)
        for artista in animados: artista.set_animated(False)
        self._fondo,self._animados = None,[]
        try:
            with writer.saving(self.fig,str(destino),dpi=100):
                for n in np.linspace(0,len(self.vista.tiempos)-1,301):
                    self.mover(n); writer.grab_frame()
            self.log.insert('end','\nMovie guardada: '+str(destino)+'\n')
        except Exception as e:
            messagebox.showerror('No se pudo exportar',str(e))
        finally:
            self.mover(previo)
            self.optimizar_dibujo()


if __name__ == '__main__':
    root = tk.Tk()
    Ventana(root)
    root.mainloop()
