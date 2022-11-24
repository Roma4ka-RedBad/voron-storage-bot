"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.clearConsole = exports.question = exports.selectFromArray = exports.trace = exports.bgColors = exports.colors = void 0;
const locale_1 = require("./locale");
const input = require('prompt-sync')({ sigint: true });
var colors;
(function (colors) {
    colors["reset"] = "\u001B[0m";
    colors["bright"] = "\u001B[1m";
    colors["dim"] = "\u001B[2m";
    colors["underscore"] = "\u001B[4m";
    colors["blink"] = "\u001B[5m";
    colors["reverse"] = "\u001B[7m";
    colors["hidden"] = "\u001B[8m";
    colors["black"] = "\u001B[30m";
    colors["red"] = "\u001B[31m";
    colors["green"] = "\u001B[32m";
    colors["yellow"] = "\u001B[33m";
    colors["blue"] = "\u001B[34m";
    colors["magenta"] = "\u001B[35m";
    colors["cyan"] = "\u001B[36m";
    colors["white"] = "\u001B[37m";
    colors["crimson"] = "\u001B[38m";
})(colors = exports.colors || (exports.colors = {}));
var bgColors;
(function (bgColors) {
    bgColors["black"] = "\u001B[40m";
    bgColors["red"] = "\u001B[41m";
    bgColors["green"] = "\u001B[42m";
    bgColors["yellow"] = "\u001B[43m";
    bgColors["blue"] = "\u001B[44m";
    bgColors["magenta"] = "\u001B[45m";
    bgColors["cyan"] = "\u001B[46m";
    bgColors["white"] = "\u001B[47m";
    bgColors["crimson"] = "\u001B[48m";
})(bgColors = exports.bgColors || (exports.bgColors = {}));
function trace(text, options) {
    if (!text) {
        return text;
    }
    options = Object.assign({
        center: false,
        textColor: colors.white,
        bgColor: bgColors.black,
        isProgress: false,
        localeStrings: []
    }, options ? options : {});
    if (options.localeStrings) {
        text = locale_1.locale.format(text, options.localeStrings);
    }
    const lines = text.split('\n');
    for (let lineIndex = 0; lines.length > lineIndex; lineIndex++) {
        const line = lines[lineIndex];
        if (options.center) {
            process.stdout.write(' '.repeat((process.stdout.columns / 2) - (line.length / 2)));
        }
        if (options.isProgress) {
            process.stdout.clearLine(0);
            process.stdout.cursorTo(0);
            process.stdout.write('\r' + options.textColor + line + colors.reset);
        }
        else {
            console.log(options.textColor + options.bgColor + line + colors.reset);
        }
    }
}
exports.trace = trace;
function selectFromArray(namesList, descriptionList = []) {
    for (let nameIndex = 0; namesList.length > nameIndex; nameIndex++) {
        const name = namesList[nameIndex];
        const description = descriptionList[nameIndex];
        let text = ` ${nameIndex + 1}. ${name}`;
        if (description) {
            text += ' '.repeat(Math.floor(process.stdout.columns / 2) - text.length) + ': ' + description;
        }
        console.log(text);
    }
    const choice = parseInt(input('>>> '), 10);
    if (choice && choice - 1 <= namesList.length) {
        return choice - 1;
    }
    else {
        return selectFromArray(namesList, descriptionList);
    }
}
exports.selectFromArray = selectFromArray;
function question(message) {
    let answer;
    while (!'ny'.includes(answer)) {
        answer = input(`[????] ${message} [Y/n] `).toLowerCase();
    }
    return 'ny'.indexOf(answer) ? true : false;
}
exports.question = question;
function clearConsole() {
    process.stdout.write('\u001b[3J\u001b[2J\u001b[1J');
    console.clear();
}
exports.clearConsole = clearConsole;
