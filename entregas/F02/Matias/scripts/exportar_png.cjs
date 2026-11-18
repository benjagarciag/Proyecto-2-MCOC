const fs = require('node:fs/promises');
const path = require('node:path');

const sharp = require(process.argv[2] || 'sharp');
const folder = path.resolve(__dirname, '..', 'figuras');

async function main() {
  const names = (await fs.readdir(folder)).filter(name => name.endsWith('.svg'));
  for (const name of names) {
    const input = path.join(folder, name);
    const output = path.join(folder, name.replace(/\.svg$/, '.png'));
    await sharp(input, {density: 108}).png().toFile(output);
  }
  console.log(`${names.length} figuras PNG exportadas`);
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
