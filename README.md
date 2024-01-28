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

You can also see the demo and try it out at [@raj/smearhash](https://piyushraj.org/smearhash).


## How does it work?

In short, SmearHash takes a video, and gives you a short list of strings (only 20-30 characters!) that represents the placeholder for that video. You do this on the backend of your service, and store the strings list along with the video. When you send media to your client, you send both the URL to the video, and the SmearHash strings list. Your client then takes the list, and decodes it into an video that it shows while the real video is loading over the network. The strings are short enough that it comfortably fits into whatever data format you use. For instance, it can easily be added as a field in a JSON object.

### In summary:

Want to know all the gory technical details? Read the [algorithm description](Algorithm.md).

Implementing the algorithm is actually quite easy! Implementations are short and easily ported to your favourite language or platform.

## Implementations

So far, we have created these implementations:

* [JavaScript](jSmearHash) - Decoder implementation, animation library and a demo.
* [Python](smearhash) - Encoder and decoder implementations, and a larger library offering advanced features.

These cover our use cases, but could probably use polishing, extending and improving. There are also these third party implementations that we know of:

* _Your designed implementation here?_

Can't find the language you're looking for? Try your luck with the GitHub search. For example, here are the search results for [repos which have "smearhash" in their name](https://github.com/search?q=smearhash+in%3Aname&type=repositories).

Perhaps you'd like to help extend this list? Which brings us to...

## Contributing

We'd love contributions! The algorithm is [very simple](Algorithm.md) - less than two hundred lines of code - and can easily be
ported to your platform of choice. And having support for more platforms would be wonderful! So, Java decoder? Golang encoder?
Haskell? Rust? We want them all!

We will also try to tag any issues on our [issue tracker](https://github.com/0x48piraj/smearhash/issues) that we'd love help with, so
if you just want to dip in, go have a look.

You're welcome to submit a pull request to our repository or initiate your own project to handle everything independently (just mention us for reference). We're open to both options.


## Users

Who uses SmearHash? Here are some projects we know about:

* I'm ofcourse using it myself. SmearHashes are used in different personal projects as placeholders during video loading.


* _Your name here?_


### Fun fact

The project got its name from a technique called [Smear framing](https://en.wikipedia.org/wiki/Smear_frame).
