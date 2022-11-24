"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.config = void 0;
const fs = require("fs");
const supercell_swf_1 = require("supercell-swf");
const other_1 = require("./features/other");
const locale_1 = require("./locale");
class Config {
    constructor() {
        this.version = require('./../package.json').version;
        this.defaultCompression = supercell_swf_1.COMPRESSION.FAST_LZMA;
        this.language = 'en-EU';
    }
    initialize() {
        if (fs.existsSync('./config.json')) {
            const configFile = require('../config.json');
            Object.assign(this, configFile);
            locale_1.locale.load(this.language);
        }
        else {
            this.language = locale_1.locale.change();
            (0, other_1.makeDirs)();
            this.dump();
        }
    }
    selectLanguage() {
        this.language = locale_1.locale.change();
        locale_1.locale.load(this.language);
        this.dump();
    }
    selectCompression() {
    }
    dump() {
        fs.writeFileSync('./config.json', JSON.stringify({
            version: this.version,
            language: this.language
        }));
    }
}
exports.config = new Config();
