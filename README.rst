DIYRSS
======

http://diyrss.unterwaditzer.net

A simple (Atom) feed generator. Enter the URL you want to scrape the HTML from,
a CSS selector that includes all articles, one for the title inside of an
article and one for the content.

Example for GitHub Gist comments::

    URL: https://gist.github.com/untitaker/5321447
    Main selector: .comment
    Title selector: .comment-header-author
    Content selector: .comment-content

Only the content's HTML will be preserved. If you want RSS, you can suck it.

Released under public domain.
