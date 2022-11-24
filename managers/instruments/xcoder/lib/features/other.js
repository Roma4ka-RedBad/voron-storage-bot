"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.exit = exports.makeDirs = exports.selectLanguage = void 0;
const console_1 = require("../console");
const config_1 = require("../config");
const fs = require("fs");
const constants_1 = require("../constants");
function selectLanguage() {
    (0, console_1.clearConsole)();
    config_1.config.selectLanguage();
}
exports.selectLanguage = selectLanguage;
function makeDirs() {
    for (const folder of constants_1.DIRS) {
        if (fs.existsSync(folder)) {
            fs.rmSync(folder, { recursive: true, force: true });
        }
        fs.mkdirSync(folder);
    }
}
exports.makeDirs = makeDirs;
function exit() {
    (0, console_1.clearConsole)();
    process.exit();
}
exports.exit = exit;
