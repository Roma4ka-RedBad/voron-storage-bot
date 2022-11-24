let textures = require("./lib/features/textures");
if (process.argv[2] == 'decode') {
	textures.texturesDecode({inPath: process.argv[3], outPath: process.argv[4], output: false})
} else {
	textures.textureEncode({inPath: process.argv[3], outPath: process.argv[4], output: false})
}
