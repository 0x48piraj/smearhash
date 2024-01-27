# SmearHash

In today's era, video dominates our world. SmearHash is a compact representation of a placeholder for a video. It's similar to BlurHash but with the following advantages:

- Encodes more detail in the same space
- Encodes the aspect ratio
- Gives more accurate colors
- **It's for videos!**


## Why would you want this?

- Does your designer cry every time you load their beautifully designed screen, which is full of empty boxes because all the videos have not loaded yet?

- Does your database engineer cry when you want to solve this by trying to cram little video reels into your data to show as placeholders?

**SmearHash** will solve your problems! How? Like this:

<p align="center">
    <img src="https://raw.githubusercontent.com/woltapp/blurhash/master/Media/WhyBlurHash.png" />
    <sub>Credits to <a href="https://github.com/woltapp/blurhash" target="_blank">@WoltApp/BlurHash</a> developers for this, clearly I am no designer.</sup>
</p>


## Is this only useful as a video-loading placeholder?

Well, that is what it's designed for originally, but it turns out to be useful for a few other things:

- Masking videos without having to use expensive blurs

- The data representation makes it quite easy to extract color features of the video for different areas.

You can also see nice examples and try them out at [@raj/blurhash](https://piyushraj.org/blurhash).


## How does it work?

In short, SmearHash takes a video, and gives you a short list of strings (only 20-30 characters!) that represents the placeholder for that video. You do this on the backend of your service, and store the strings list along with the video. When you send media to your client, you send both the URL to the video, and the SmearHash strings list. Your client then takes the list, and decodes it into an video that it shows while the real video is loading over the network. The strings are short enough that it comfortably fits into whatever data format you use. For instance, it can easily be added as a field in a JSON object.

#### In summary:

Want to know all the gory technical details? Read the [algorithm description](Algorithm.md).

Implementing the algorithm is actually quite easy! Implementations are short and easily ported to your favourite language or platform.


### Fun fact

The project got its name from a technique called [Smear framing](https://en.wikipedia.org/wiki/Smear_frame).
