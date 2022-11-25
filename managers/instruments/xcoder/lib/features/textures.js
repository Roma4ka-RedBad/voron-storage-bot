"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.textureEncode = exports.texturesDecode = void 0;
const prompt = require('prompt-sync')({ sigint: true });
const fs = require("fs");
const path = require("path");
const process_1 = require("process");
const supercell_swf_1 = require("supercell-swf");
const utils_1 = require("./utils");
const PNG = require("fast-png");
const image_js_1 = require("image-js");
const config_1 = require("../config");
const console_1 = require("../console");
const locale_1 = require("../locale");
function texturesDecode(options = { inPath: undefined, outPath: undefined, output: true }) {
    if (!options.inPath || !options.outPath) {
        throw new Error('Path not specified!');
    }
    const file = options.inPath;
    console.log(file);
    if (file.endsWith('_tex.sc')) {
        const startTime = (0, process_1.hrtime)();
        const folder = `${options.outPath}/${path.parse(file).name}`;
        if (fs.existsSync(folder)) {
            fs.rmSync(folder, { recursive: true, force: true });
        }
        fs.mkdirSync(folder);
        const infoFile = [];
        const swf = (0, utils_1.createSWF)(options.output).loadExternalTexture(file);
        (0, console_1.trace)(locale_1.locale.imageSaving, { textColor: console_1.colors.green });
        for (let i = 0; swf.textures.length > i; i++) {
            const texture = swf.textures[i];
            fs.writeFileSync(`${folder}/${path.parse(file).name}${'_'.repeat(i)}.png`, texture.image.toBuffer());
            infoFile.push(texture.toJSON());
        }
        fs.writeFileSync(`${folder}/${path.parse(file).name}.json`, JSON.stringify(infoFile, null, 2));
    }
}
exports.texturesDecode = texturesDecode;
function textureEncode(options = { inPath: undefined, outPath: undefined, output: true }) {
    const startTime = (0, process_1.hrtime)();
    const swf = (0, utils_1.createSWF)(options.output);
    swf.compression = config_1.config.defaultCompression;
    const folder = options.inPath;
    const folderName = path.parse(folder).name;
    const dirContent = fs.readdirSync(folder);
    const texturesInfo = dirContent.includes(`${folderName}.json`) ? require(`${path.resolve(folder)}/${folderName}.json`) : [];
    let textureIndex = 0;
    for (const file of dirContent) {
        if (file.endsWith('.png')) {
            const texture = new supercell_swf_1.Texture();
            const image = PNG.decode(fs.readFileSync(`${folder}/${file}`));
            texture.image = new image_js_1.Image(image.width, image.height, image.data, {
                components: image.channels % 2 === 0 ? image.channels - 1 : image.channels,
                alpha: image.channels % 2 === 0 ? 1 : 0,
                bitDepth: image.depth,
            });
            const textureInfo = texturesInfo[textureIndex];
            if (textureInfo !== undefined) {
                const width = textureInfo.width;
                const height = textureInfo.height;
                if (width && height) {
                    if (width !== texture.width || height !== texture.height) {
                        let resize = true;
                        if (!resize) {
                            textureInfo.width = texture.width;
                            textureInfo.height = texture.height;
                        }
                    }
                }
                texture.fromJSON(textureInfo);
            }
            swf.textures.push(texture);
            textureIndex++;
        }
    }
    swf.saveExternalTexture(options.outPath, false);
}
exports.textureEncode = textureEncode;
