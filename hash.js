var torrentUrl = process.argv[2];
var torrentStream = require('torrent-stream');
var torrentHash = require('os-torrent-hash');
var engine = torrentStream(torrentUrl);
torrentHash.computeHash(torrentUrl, engine) // engine is a torrent-stream engine
    .then(function (res) {
        console.log("Movie hash: " + res.movieHash);
        console.log("File size: " + res.fileSize);
        console.log("File name: " + res.fileName);
	process.exit(code=0)
    })
    .catch(function (error) {
	process.exit(code=1)
    })
    .done();
