let jSmearHash = function() {

    const digit =
    '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz#$%*+,-.:;=?@[]^_{|}~';
    const decode83 = (str, start, end) => {
        let value = 0;
        while (start < end) {
            value *= 83;
            value += digit.indexOf(str[start++]);
        }
        return value;
    };

    const pow = Math.pow;
    const PI = Math.PI;
    const PI2 = PI * 2;

    const d = 3294.6;
    const e = 269.025;
    const sRGBToLinear = (value) =>
        value > 10.31475 ? pow(value / e + 0.052132, 2.4) : value / d;

    const linearTosRGB = (v) =>
        ~~(v > 0.00001227 ? e * pow(v, 0.416666) - 13.025 : v * d + 1);

    const signSqr = (x) => (x < 0 ? -1 : 1) * x * x;

    /**
     * Fast approximate cosine implementation
     * Based on FTrig https://github.com/netcell/FTrig
     */
    const fastCos = (x) => {
        x += PI / 2;
        while (x > PI) {
            x -= PI2;
        }
        const cos = 1.27323954 * x - 0.405284735 * signSqr(x);
        return 0.225 * (signSqr(cos) - cos) + cos;
    };

    /**
     * Extracts average color from BlurHash image
     * @param {string} blurHash BlurHash image string
     * @returns {[number, number, number]}
     */
    function getBlurHashAverageColor(blurHash) {
        const val = decode83(blurHash, 2, 6);
        return [val >> 16, (val >> 8) & 255, val & 255];
    }

    /**
     * Decodes BlurHash image
     * @param {string} blurHash BlurHash image string
     * @param {number} width Output image width
     * @param {number} height Output image height
     * @param {?number} punch
     * @returns {Uint8ClampedArray}
     */
    function decodeBlurHash(blurHash, width, height, punch) {
        const sizeFlag = decode83(blurHash, 0, 1);
        const numX = (sizeFlag % 9) + 1;
        const numY = ~~(sizeFlag / 9) + 1;
        const size = numX * numY;

        let i = 0,
            j = 0,
            x = 0,
            y = 0,
            r = 0,
            g = 0,
            b = 0,
            basis = 0,
            basisY = 0,
            colorIndex = 0,
            pixelIndex = 0,
            yh = 0,
            xw = 0,
            value = 0;

        const maximumValue = ((decode83(blurHash, 1, 2) + 1) / 13446) * (punch | 1);

        const colors = new Float64Array(size * 3);

        const averageColor = getBlurHashAverageColor(blurHash);
        for (i = 0; i < 3; i++) {
            colors[i] = sRGBToLinear(averageColor[i]);
        }

        for (i = 1; i < size; i++) {
            value = decode83(blurHash, 4 + i * 2, 6 + i * 2);
            colors[i * 3] = signSqr(~~(value / (19 * 19)) - 9) * maximumValue;
            colors[i * 3 + 1] = signSqr((~~(value / 19) % 19) - 9) * maximumValue;
            colors[i * 3 + 2] = signSqr((value % 19) - 9) * maximumValue;
        }

        const bytesPerRow = width * 4;
        const pixels = new Uint8ClampedArray(bytesPerRow * height);

        for (y = 0; y < height; y++) {
            yh = (PI * y) / height;
            for (x = 0; x < width; x++) {
                r = 0;
                g = 0;
                b = 0;
                xw = (PI * x) / width;

                for (j = 0; j < numY; j++) {
                    basisY = fastCos(yh * j);
                    for (i = 0; i < numX; i++) {
                        basis = fastCos(xw * i) * basisY;
                        colorIndex = (i + j * numX) * 3;
                        r += colors[colorIndex] * basis;
                        g += colors[colorIndex + 1] * basis;
                        b += colors[colorIndex + 2] * basis;
                    }
                }

                pixelIndex = 4 * x + y * bytesPerRow;
                pixels[pixelIndex] = linearTosRGB(r);
                pixels[pixelIndex + 1] = linearTosRGB(g);
                pixels[pixelIndex + 2] = linearTosRGB(b);
                pixels[pixelIndex + 3] = 255; // alpha
            }
        }
        return pixels;
    }

    let args = {
        debug: false,
        hashList: false,
        container: false,
        columns: false,
        rows: false,
        autoStart: false,
        repeat: true,
        startFrame: false,
        length: false,
        timing: false,
        timings: false,
        widthOffset: 0,
        onStart: false,
        onStop: false,
        onProgress: false,
        onComplete: false,
        onRepeat: false,
    };
    // - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    // process arguments
    if (arguments[0] && typeof(arguments[0]) == "object") {
        for (var key in arguments[0]) {
            if (args.hasOwnProperty(key)) {
                let v = arguments[0][key];
                if (v == undefined) {
                    args[key] = false;
                } else {
                    args[key] = arguments[0][key];
                }
            }
        }
    }
    // - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


    let vars = {
        dom: {
            container: false
        },
        img: false,
        spriteSheetW: 0,
        spriteSheetH: 0,
        frameW: 0,
        frameH: 0,

        startFrame: 0,
        endFrame: 0,
        length: 0,
        maxFrames: 0,
        noOfFramesToPlay: 0,

        frame: 1,
        frames: [],
        stopRequested: false,
        bg: false,
        dispose: false,
        status: "stopped", // playing, stopped
    };
    // - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


    function constructor() {
        // log("jSmearHash.constructor()");

        // validate args
        if (args.startFrame < 1) {
            args.startFrame = 1;
        }

        if (args.hashList === false) {
            console.error("jSmearHash.js: usage error: you must specify a sprite sheet hash to use!");
            return;
        }

        if (args.container === false) {
            console.error("jSmearHash.js: usage error: you must specify a container (must be an element id");
            return;
        }

        if (args.columns === false) {
            console.error("jSmearHash.js: usage error: you must specify the no' of frames (columns) on the x axis!");
            return;
        }

        if (args.rows === false) {
            console.error("jSmearHash.js: usage error: you must specify the no' of frames (rows) on the y axis!");
            return;
        }

        // if (args.noOfFrames === false){
        //     console.error("jSmearHash.js: usage error: you must specify the no' of frames!");
        //     return;
        // }

        if (args.timing === false && args.timings === false) {
            console.error("jSmearHash.js: usage error: you must specify either timing or timings for each frame!");
            return;
        }

        // convert hashes into sprite grid
        var idx = 0, number_of_images = args.hashList.length;
        const hvconcat_image_width = 1024; // by default
        var frame_image_width = 144; // this should be coded into the list?
        var frame_image_height = 144;
        const images_per_row_in_hvconcat = parseInt(Math.round(Math.sqrt(number_of_images)))

        if (number_of_images == 0) {
            console.error("jSmearHash.js: Can not make a hvconcat of zero images!");
            return;
        }

        const scale = (hvconcat_image_width) / (
            images_per_row_in_hvconcat * frame_image_width
        )

        var scaled_frame_image_width = Math.ceil(frame_image_width * scale)
        var scaled_frame_image_height = Math.ceil(frame_image_height * scale)

        var number_of_rows = Math.ceil(number_of_images / images_per_row_in_hvconcat)

        var hvconcat_image_height = Math.ceil(scale * frame_image_height * number_of_rows)

        const hvconcat_image = document.createElement('canvas');
        const ctx = hvconcat_image.getContext('2d');
        hvconcat_image.width = hvconcat_image_width;
        hvconcat_image.height = hvconcat_image_height;

        var i =0, j =0;
        var x, y;
        while (idx < number_of_images) {
            if ((idx % images_per_row_in_hvconcat) == 0)
            {
                i = 0;
            }

            // decode blurHash image
            var pixels = decodeBlurHash(args.hashList[idx], scaled_frame_image_width, scaled_frame_image_height);
            x = i
            y = ~~(j / images_per_row_in_hvconcat) * scaled_frame_image_height
            // draw the frame image on frame canvas
            var imageData = new ImageData(pixels, scaled_frame_image_width, scaled_frame_image_height);
            ctx.putImageData(imageData,x,y);
            i = i + scaled_frame_image_width
            j += 1
            idx++
        }

        // document.body.append(canvas);
        // load sprite sheet image
        vars.img = new Image();
        vars.img.onload = imageLoaded;
        vars.img.src = hvconcat_image.toDataURL();
    }
    // - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -



    function imageLoaded(e) {
        // log("jSmearHash.imageLoaded(e)");
        // log(e.target);

        // we can now get the width and height of the sprite sheet calculate vars
        vars.spriteSheetW = e.target.width;
        vars.spriteSheetH = e.target.height;

        // log("e.target.width = " + e.target.width + "    e.target.height = " + e.target.height);
        vars.frameW = Math.ceil(e.target.width / args.columns);
        vars.frameH = Math.ceil(e.target.height / args.rows);

        // setup css background on container from img src
        let bg = "url(" + e.target.src + ")";


        vars.dom.container = document.getElementById(args.container);
        // vars.dom.container.style.background = "#FFCC00";
        vars.dom.container.style.backgroundImage = bg;
        vars.dom.container.style.backgroundRepeat = "no-repeat";
        vars.dom.container.style.backgroundPosition = "0px 0px";
        vars.dom.container.style.width = vars.frameW + "px";
        vars.dom.container.style.height = vars.frameH + "px";


        // log("jSmearHash.initVars()");
        vars.xLim = vars.spriteSheetW / vars.frameW;
        vars.yLim = vars.spriteSheetH / vars.frameH;

        // handle width offset
        vars.frameW += args.widthOffset;

        // log("frameW = " + vars.frameW + "   frameH = " + vars.frameH);
        vars.dom.container.style.width = vars.frameW + "px";
        vars.dom.container.style.height = vars.frameH + "px";

        // Limits
        vars.maxFrames = args.columns * args.rows;
        // log("vars.maxFrames = " + vars.maxFrames);


        calcVars();


        // Calculate all frames and background positions
        // NOTE: This was done in timing loop but to make start frame and end frame playback easier
        // the control to get specific frame from vars.frames by index (index = frame no you want)
        // is easier

        let frame = 0;
        for (let row = 0; row < args.rows; row++) {
            for (let col = 0; col < args.columns; col++) {
                frame++;
                let x = 0 - (col * vars.frameW);
                let y = 0 - (row * vars.frameH);

                // let msg = "";
                // msg += "row:" + row + "   ";
                // msg += "col:" + col + "   ";
                // msg += "x:" + x + "   ";
                // msg += "y:" + y + "   ";
                // log(msg);

                vars.frames.push([x, y]);
            }
        }
        // log(vars.frames);

        // log(args);
        // log(vars);

        vars.frame = vars.startFrame;

        // position sprite at first frame
        let startPos = vars.frames[(vars.startFrame - 1)];
        let x = startPos[0];
        let y = startPos[1];
        vars.dom.container.style.backgroundPosition = x + "px " + y + "px";



        if (args.debug) {
            // log("jSmearHash: init");
            log("frameW:" + vars.frameW + "   frameH:" + vars.frameH);
            log("cols:" + args.columns + "   rows:" + args.rows);
            log("startPos: " + startPos);
        }


        if (args.autoStart) {
            if (args.onStart !== false) {
                args.onStart();
            }
            animate();
        }


    }
    // - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -





    function calcVars() {
        // Handle args start frame
        if (args.startFrame === false) {
            vars.startFrame = 1;
        } else {
            vars.startFrame = parseInt(args.startFrame);
            if (vars.startFrame < 0) {
                vars.startFrame = 1;
            }
        }


        // handle length
        if (args.length !== false && typeof(args.length) == "number") {
            vars.length = args.length;

            // check no of frames from startFrame can handle the length
            let possibleEndFrame = vars.startFrame + vars.length - 1;
            if (possibleEndFrame > vars.maxFrames) {
                // user is trying to play past the number of frames available!
                let msg = "jSmearHash: You have set a playback length of [" + args.length + "] from a ";
                msg += "starting frame of [" + vars.startFrame + "].";
                msg += " No enough frames to play! RESETTING playback to first and last frames on sprite src[";
                msg += args.hashList + "]";
                console.error(msg);
                vars.startFrame = 1;
                vars.length = vars.maxFrames;
            }
        } else {
            vars.length = vars.maxFrames;
        }


        // work out number of frames to play
        vars.noOfFramesToPlay = vars.startFrame + (vars.length - 1)


        // work out end frame
        vars.endFrame = vars.startFrame + vars.length - 1;
        if (vars.endFrame > vars.maxFrames) {
            vars.endFrame = vars.maxFrames;
        }


        // log("AFTER:");
        if (args.debug) {
            log("jSmearHash: calc");
            log("maxFrames = " + vars.maxFrames);
            log("startFrame = " + vars.startFrame + "   vars.endFrame = " + vars.endFrame);
            log("vars.length = " + vars.length + "    vars.noOfFramesToPlay = " + vars.noOfFramesToPlay);
        }
    }
    // - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -





    function animate() {
        // Stop for dispose
        if (this.dispose === true) {
            return;
        }

        // Handle stop request
        if (vars.stopRequested === true) {
            vars.stopRequested = false;
            vars.status = "stopped";

            if (args.onStop !== false) {
                args.onStop();
            }
            return;
        }


        if (args.repeat === true) {
            if (vars.frame > vars.endFrame) {
                vars.frame = vars.startFrame;
            }
        }


        // playback
        vars.status = "playing";

        // log(vars.frame);
        let fTime = getFrameTime();
        let framePos = vars.frames[vars.frame - 1];

        let msg = "";
        msg += vars.frame + "/" + vars.maxFrames + "   ";
        msg += framePos + "   ";
        // msg += "fTime:" + fTime + "   ";
        msg += "frames.len = " + vars.frames.length + "   ";
        // log(msg);
        // html("debug1",msg);


        let x = framePos[0];
        let y = framePos[1];
        vars.dom.container.style.backgroundPosition = x + "px " + y + "px";



        if (args.onProgress !== false) {
            let o = {
                frame: vars.frame,
                totalFrames: vars.maxFrames
            }
            args.onProgress(o);
        }


        // Move on
        vars.frame++;
        if (vars.frame <= vars.endFrame) {
            setTimeout(animate, fTime);
        } else {
            vars.frame = vars.startFrame;

            if (args.repeat) {

                if (args.onRepeat !== false) {
                    args.onRepeat();
                }

                setTimeout(animate, fTime);
            } else {
                if (args.onComplete !== false) {
                    args.onComplete();
                }

                vars.status = "stopped";
            }
        }
    }
    // - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -




    function getFrameTime() {
        // timing vars
        if (args.timing !== false) {
            // timing is constant
            return args.timing

        } else {
            // timing is array based must be same size as frames
            let t = args.timings[(vars.frame - 1)];
            // log(vars.frame + " : " + t);
            if (!t) {
                t = 1000;
            }
            return t;
        }
    }
    // - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -



    function restart() {
        // log("jSmearHash.restart()");
        // log(vars.status);

        vars.frame = vars.startFrame;
        if (vars.status == "stopped") {
            animate();
        }
    }



    function start() {
        // log("jSmearHash.start(): vars.status = " + vars.status);
        if (vars.status != "playing") {

            if (args.onStart !== false) {
                args.onStart();
            }

            animate();
        }
    }
    // - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -




    function stop() {
        // log("jSmearHash.stop()");
        vars.stopRequested = true;
    }
    // - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


    // UTILS
    // - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    function log(arg) {
        console.log(arg);
    }

    function convertUndefinedToFalse(v) {
        if (v == undefined) {
            v = false;
        };
    }

    function html(id, value) {
        let element = document.getElementById(id);
        if (element) {
            element.innerHTML = value;
        }
    }
    // - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -



    // PUBLIC
    // - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    this.start = function() {
        start();
    }

    this.stop = function() {
        stop();
    }

    this.restart = function() {
        restart();
    }



    this.setStartFrame = function(v) {
        if (args.debug) {
            console.clear();
            log("jSmearHash.setStartFrame(v:" + v + ")");
        }


        args.startFrame = v;
        args.length = false;
        vars.length = false;
        vars.frame = args.startFrame;
        calcVars();
    }

    this.setLength = function(v) {

        if (args.debug) {
            console.clear();
            log("jSmearHash.setLength(v:" + v + ")");
        }

        args.length = v;
        vars.length = v;
        vars.frame = vars.startFrame;
        calcVars();
    }

    this.dispose = function() {
        vars.dispose = true;
        delete vars;
        delete args;
        delete setLength;
        delete setStartFrame;
        delete start;
        delete stop;
        delete restart;
    }
    // - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -




    // Constructor simulation
    constructor();
    // - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
}