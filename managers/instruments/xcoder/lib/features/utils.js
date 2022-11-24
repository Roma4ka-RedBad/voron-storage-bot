"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.createTexture = exports.createSWF = void 0;
const supercell_swf_1 = require("supercell-swf");
const console_1 = require("../console");
const locale_1 = require("../locale");
const path = require("path");
const PNG = require("fast-png");
const image_js_1 = require("image-js");
const fs = require("fs");
function createSWF(output = true) {
    const swf = new supercell_swf_1.SupercellSWF();
    swf.progress = output ? function (state, property) {
        switch (state) {
            case supercell_swf_1.STATES.resources_load:
                break;
            case supercell_swf_1.STATES.resources_save:
                break;
            case supercell_swf_1.STATES.texture_save:
            case supercell_swf_1.STATES.texture_load:
                (0, console_1.trace)(locale_1.locale.aboutTexture, {
                    textColor: console_1.colors.green, localeStrings: [
                        property[0],
                        property[1],
                        swf.textures[property[1]].pixelFormat,
                        swf.textures[property[1]].width,
                        swf.textures[property[1]].height
                    ], isProgress: true
                });
                break;
            case supercell_swf_1.STATES.loading:
                (0, console_1.trace)(locale_1.locale.format(locale_1.locale.fileLoading, [path.parse(property).base]));
                break;
            case supercell_swf_1.STATES.saving:
                (0, console_1.trace)(locale_1.locale.format(locale_1.locale.fileSaving, [path.parse(property).base]));
                break;
        }
    } : function (state, property) { };
    return swf;
}
exports.createSWF = createSWF;
function createTexture(filepath) {
    const texture = new supercell_swf_1.Texture();
    const image = PNG.decode(fs.readFileSync(filepath));
    switch (image.channels) {
        case 1:
            texture.pixelFormat = supercell_swf_1.CHANNEL_FORMATS['GREY'][0];
            break;
        case 2:
            texture.pixelFormat = supercell_swf_1.CHANNEL_FORMATS['GREYA'][0];
            break;
        case 3:
            texture.pixelFormat = supercell_swf_1.CHANNEL_FORMATS['RGB'][0];
            break;
        case 4:
            texture.pixelFormat = supercell_swf_1.CHANNEL_FORMATS['RGBA'][0];
            break;
    }
    texture.image = new image_js_1.Image(image.width, image.height, image.data, {
        components: image.channels % 2 === 0 ? image.channels - 1 : image.channels,
        alpha: image.channels % 2 === 0 ? 1 : 0,
        bitDepth: image.depth,
    });
    return texture;
}
exports.createTexture = createTexture;
