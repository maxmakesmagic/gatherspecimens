# Wizards article information

This doc is a brief overview of the information gathered while researching the Wizards.com website.

## www.wizards.com/default.asp - January 1, 2002

The original Wizards website was dynamically served through `default.asp` with the `x` query parameter specifying the requested article.

The vast majority of articles can be seen in the Wayback machine using the [`mtgcom/fullarchive`](https://web.archive.org/web/20080518031038/http://www.wizards.com/default.asp?x=mtgcom/fullarchive) query parameter - the last successful gathering was May 18, 2008.

The article "In the Beginning...", which announced the new site, was released on January 2 2002, but according to the article timestamps the first article was "On Your Mark... Get Set... Radiate!", written on January 1 2002 by Anthony Alongi.

## www.wizards.com/Magic/Magazine/ - August 26, 2008

The transition to the new MagicTheGathering.com happened around August 26, 2008, as per [Welcome to the New Magicthegathering.com](https://web.archive.org/web/20080831014057/http://www.wizards.com/Magic/Magazine/Article.aspx?x=mtg/daily/news/082608) article.

The second Wizards website operated similarly to the first, in that articles were dynamically served through `Article.aspx` with the `x` query parameter specifying the requested article. Additional pages were available at a variety of .aspx pages, for example `Events.aspx`, `News.aspx` and `Hall of Fame.aspx`.

## magic.wizards.com - June 17, 2014

magic.wizards.com released in June of 2014 with [Welcome to the New Magic Site!](https://web.archive.org/web/20140621150155/http://magic.wizards.com/en/articles/archive/welcome-new-magic-site-2014-06-17).

It uses Drupal 7 as a content management system, as evidenced by the meta:generator tags. It uses a custom theme called `wiz_mtg`.

Notable changes:

- between September 1, 2017 and September 9, 2017: `https://` became the default on the Wizards website.
- between August 22, 2018 and August 27, 2018: the `wiz_mtg` theme changed and the reported `length` parameter in Wayback reports went up from ~20KB to ~80KB. This is seemingly due to Wizards embedding complex SVG logos directly into the webpage.

## magic.wizards.com 2, Electric Boogaloo - November 8, 2022

With the announcement [A New Daily(MTG)](https://magic.wizards.com/en/news/announcements/a-new-daily-mtg), DailyMTG was switched from its Drupal backend to the same backend system that powered `Magic.gg`.

This appears to be [Contentful](https://contentful.com), as can be seen by `images.ctfassets.net/` URLs in the source code.

Many articles were not migrated as part of this switch to Contentful, which necessitated the creation of the [Ormos project](https://github.com/maxmakesmagic/ormos).
