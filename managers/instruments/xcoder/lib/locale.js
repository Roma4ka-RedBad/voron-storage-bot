"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.locale = void 0;
const fs = require("fs");
const path = require("path");
const console_1 = require("./console");
const input = require('prompt-sync')({ sigint: true });
class Locale {
    format(localeString, localeStrings = []) {
        let i = 0;
        if (localeString) {
            return localeString.replace(/%s/g, () => localeStrings[i++]);
        }
        else {
            return localeString;
        }
    }
    load(language) {
        const languagePath = `${__dirname}/locales/${language}.json`;
        const defaultLanguagePath = `${__dirname}/locales/en-EU.json`;
        let languageLocale;
        if (fs.existsSync(languagePath)) {
            languageLocale = require(languagePath);
        }
        else {
            languageLocale = require(defaultLanguagePath);
        }
        Object.assign(this, languageLocale);
    }
    change() {
        const locales = fs.readdirSync(`${__dirname}/locales/`);
        console.log('Select language:\n');
        const languageSelected = (0, console_1.selectFromArray)(locales.map(localeFile => { return path.parse(localeFile).name; }));
        if (locales[languageSelected]) {
            this.load(path.parse(locales[languageSelected]).name);
        }
        else {
            return this.change();
        }
        return path.parse(locales[languageSelected]).name;
    }
}
exports.locale = new Locale();
