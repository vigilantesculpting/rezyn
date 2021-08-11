%----------------------------------------------------------------------
%- Functions for the RSS feeds
%----------------------------------------------------------------------

%func item: path post
	%set 'postlink': config/site_url config/tgtsubdir path post/slug '.html' + //+
<item>
	<title>{{ post/title }}</title>
	<link>{{ postlink }}</link>
	<description>
		<![CDATA[
		<p>
		%if post/thumbnail exists
			<a class="more" href="{{ postlink }}">{{ post/thumbnail }}</a>
		%end
		{{ post/content truncate }}&nbsp;<a href="{{ postlink }}">[...Read More]</a>
		</p>
	]]>
	</description>
	<tags:taglist>
	%for tag: post/tags
		<tags:tag>{{ tag }}</tags:tag>
	%end
	</tags:taglist>
	<pubDate>{{ post/date '%%a, %%d %%b %%Y %%H:%%M:%%S %%z' strftime }}</pubDate>
</item>
%end

%func feed: posts title rsspath postpath description
%output rsspath 'rss.xml' //+
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" 
	xmlns="http://backend.userland.com/rss2"
	xmlns:tags="https://vigilantesculpting.github.io/tagsModule/">
<channel>
<title>{{ title }}</title>
<link>{{ config/site_url config/tgtsubdir rsspath //+ }}</link>
<description>{{ description }}</description>
%for post: posts
	%call item: postpath post
%end
</channel>
</rss>
%end
%end

%call feed: content/sortedposts 'rezyn feed' '' 'blog' content/blog.html/content
