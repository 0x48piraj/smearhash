# jSmearHash: SmearHash Decoder & 2D Sprite Animation Library

-   **Tiny**: ≈1kB (minified)
-   **Fast**: up to 50% faster than [original `blurhash.decode`](https://github.com/woltapp/blurhash/tree/master/TypeScript#decodeblurhash-string-width-number-height-number-punch-number--uint8clampedarray) (see [benchmark](./benchmark.js))


## Usage

- Set the generated **smearhashes** of the target video to `hashList`
- Set container to the ID of the html element that will contain your sprite
- Set no of columns the sprite sheet has
- Set no of rows the sprite sheet has
- If your sprite is not aligned on the x axis correctly you can adjust the x offset viaw "widthOffset: -5"
- Set the timing of the sprite, note you can control the timings of each frame individually if you use timings and feed it an array of number matching the number of frames in your sprite.


> **Note:** jSmearHash will resize the container to the dimensions it calculates the a single sprite frame to be, if you wish to adjust size of the sprite you can use transform scale via css or javascript.


````typescript
let mySprite = new jSmearHash({
	spriteSheet: ['...', '...', '...'],
	container: "HTMLId",
	columns: 8,
	rows: 4,
	widthOffset: 0,
	startFrame: 1,
	length: 8,
	timing: 50,
	autoStart: true,
	repeat: true,
	onComplete: function,
	onProgress: function,
	onComplete: function,
	onRepeat: function,
	onStop: function
});

````


## Parameters

<table>
    <tr>
        <th>Name</th>
        <th>Type</th>
        <th></th>
        <th>Info</th>
    </tr>
    <tr>
        <td>hashList</td>
        <td>List</td>
        <td>REQUIRED</td>
        <td>The smearhashes list to the target video</td>
    </tr>
    <tr>
        <td>container</td>
        <td>String</td>
        <td>REQUIRED</td>
        <td>ID of html element to use for the sprite</td>
    </tr>
    <tr>
        <td>columns</td>
        <td>Number</td>
        <td>REQUIRED</td>
        <td>The number of columns your sprite sheet has</td>
    </tr>
    <tr>
        <td>rows</td>
        <td>Number</td>
        <td>REQUIRED</td>
        <td>The number of rows your sprite sheet has</td>
    </tr>
    <tr>
        <td>timing</td>
        <td>Number</td>
        <td>REQUIRED</td>
        <td>The delay in ms between each frame</td>
    </tr>
    <tr>
        <td>widthOffset</td>
        <td>Number</td>
        <td></td>
        <td>If the sprite is not quite divisible by it's no of columns then you can adjust it with the widthOffset</td>
    </tr>
    <tr>
        <td>startFrame</td>
        <td>Number</td>
        <td></td>
        <td>The number of which frame you would like to start on</td>
    </tr>
    <tr>
        <td>length</td>
        <td>Number</td>
        <td></td>
        <td>The number of frames you would like to play from the start frame (do not exceed max length)</td>
    </tr>
    <tr>
        <td>repeat</td>
        <td>Boolean</td>
        <td></td>
        <td>Do you want the sprite animation to repeat, yes = true, no = false, default = true</td>
    </tr>
    <tr>
        <td>onStart</td>
        <td>function</td>
        <td></td>
        <td>Function callback for when start is called</td>
    </tr>
    <tr>
        <td>onStop</td>
        <td>function</td>
        <td></td>
        <td>Function callback for when stop is called</td>
    </tr>
    <tr>
        <td>onProgress</td>
        <td>function</td>
        <td></td>
        <td>Function called for each frame setp of the sprite</td>
    </tr>
    <tr>
        <td>onRepeat</td>
        <td>function</td>
        <td></td>
        <td>Function callback for when sprite animation repeats</td>
    </tr>
    <tr>
        <td>onComplete</td>
        <td>function</td>
        <td></td>
        <td>Function callback for when sprite animation is complete</td>
    </tr>
</table>


### Methods

<table>
    <tr>
        <th>Name</th>
        <th>Info</th>
    </tr>
    <tr>
        <td>start()</td>
        <td>Starts/resumes the sprite animation</td>
    </tr>
    <tr>
        <td>stop()</td>
        <td>Stops the sprite animation</td>
    </tr>
    <tr>
        <td>restart()</td>
        <td>Restarts the sprite animation from start</td>
    </tr>
    <tr>
        <td>setStartFrame(frameIndex)</td>
        <td>Sets the sprite start frame</td>
    </tr>
    <tr>
        <td>setLength()</td>
        <td>Sets the length of the animations aka the no' of frames to play</td>
    </tr>
    <tr>
        <td>decodeBlurHash(blurhash: string, width: number, height: number, punch?: number) => Uint8ClampedArray</td>
        <td>Provides a drop-in replacement for <a href="https://github.com/woltapp/blurhash/tree/master/TypeScript#decodeblurhash-string-width-number-height-number-punch-number--uint8clampedarray">original <code>blurhash.decode</code></a>. It uses approximate calculations for speed reasons. Results may slightly differ from the original but the difference is not noticeable (see [tests](./index.test.js)). This method does not validate input (⚠️).</td>
    </tr>
    <tr>
        <td>getBlurHashAverageColor(blurhash: string) => [number, number, number]</td>
        <td>Returns an average color of a passed blurhash image in [red, green, blue].</td>
    </tr>
</table>
