"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.menu = exports.wrapText = void 0;
const input = require('prompt-sync')({ sigint: true });
const console_1 = require("./console");
const other_1 = require("./features/other");
const locale_1 = require("./locale");
const config_1 = require("./config");
const textures_1 = require("./features/textures");
const constants_1 = require("./constants");
function wrapText(text, maxlength) {
    const result = [''];
    if (maxlength >= text.length) {
        return text;
    }
    else {
        let totalStrCount = Math.floor(text.length / maxlength);
        if (text.length % maxlength !== 0) {
            totalStrCount++;
        }
        for (let i = 0; i < totalStrCount; i++) {
            if (i === totalStrCount - 1) {
                result.push(text);
            }
            else {
                const strPiece = text.substring(0, maxlength - 1);
                result.push(strPiece);
                result.push('<br>');
                text = text.substring(maxlength - 1, text.length);
            }
        }
    }
    return result.join('');
}
exports.wrapText = wrapText;
class Item {
    constructor(options) {
        this.name = 'Item name';
        this.description = 'Description';
        this.arguments = {};
        Object.assign(this, options);
    }
    run() {
        this.handler(this.arguments || arguments);
    }
}
class Category {
    constructor(name) {
        this.items = [];
        this.name = name;
    }
}
class Menu {
    constructor() {
        this.categories = [];
        const scCategory = new Category(locale_1.locale.scLabel);
        this.categories.push(scCategory);
        scCategory.items.push(new Item({
            name: locale_1.locale.scToTexture,
            description: locale_1.locale.scToTexture_description,
            handler: textures_1.texturesDecode,
            arguments: { inPath: constants_1.TEXTURE_IN_SC, outPath: constants_1.TEXTURE_OUT, output: true }
        }));
        scCategory.items.push(new Item({
            name: locale_1.locale.textureToSc,
            description: locale_1.locale.textureToSc_description,
            handler: textures_1.textureEncode,
            arguments: { inPath: constants_1.TEXTURE_IN, outPath: constants_1.TEXTURE_OUT_SC, output: true }
        }));
        const otherCategory = new Category(locale_1.locale.otherFeaturesLable);
        this.categories.push(otherCategory);
        otherCategory.items.push(new Item({
            name: locale_1.locale.clearDirs,
            description: locale_1.locale.clearDirs_description,
            handler: other_1.makeDirs
        }));
        otherCategory.items.push(new Item({
            name: locale_1.locale.changeLanguage,
            description: locale_1.locale.format(locale_1.locale.changeLanguage_description, [config_1.config.language]),
            handler: other_1.selectLanguage
        }));
        otherCategory.items.push(new Item({
            name: locale_1.locale.exit,
            description: '',
            handler: other_1.exit
        }));
    }
    printCategory(text) {
        (0, console_1.trace)(text, { textColor: console_1.colors.black, bgColor: console_1.bgColors.green });
    }
    printFeature(id, name, description = undefined, width = -1) {
        let text = ` ${id} ${name}`;
        if (description) {
            text += ' '.repeat(Math.floor(width / 2) - text.length) + ': ' + description;
        }
        console.log(wrapText(text, width));
    }
    printDividerLine(width) {
        console.log('-'.repeat(width));
    }
    choice() {
        console.clear();
        const width = process.stdout.columns;
        (0, console_1.trace)(locale_1.locale.xcoderHeader, {
            center: true, textColor: console_1.colors.green, bgColor: console_1.bgColors.black,
            localeStrings: [require('./../package.json').version]
        });
        (0, console_1.trace)('github.com/scwmake/XCoder', { center: true });
        this.printDividerLine(width);
        let itemsCounter = 1;
        const items = {};
        for (let categoryIndex = 0; this.categories.length > categoryIndex; categoryIndex++) {
            const category = this.categories[categoryIndex];
            this.printCategory(category.name);
            for (let itemIndex = 0; category.items.length > itemIndex; itemIndex++) {
                const item = category.items[itemIndex];
                items[itemsCounter] = item;
                this.printFeature(itemsCounter, item.name, item.description, width);
                itemsCounter++;
            }
            this.printDividerLine(width);
        }
        const choice = parseInt(input(locale_1.locale.choice), 10);
        this.printDividerLine(width);
        if (!choice) {
            return undefined;
        }
        if (items[choice]) {
            return items[choice];
        }
        return undefined;
    }
}
exports.menu = new Menu();
