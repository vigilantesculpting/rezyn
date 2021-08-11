%import template/page.tpl

%func postsummary: postpath post
	%set 'postlink': postpath (post/slug '.html' +) //+
	<h2><a href="{{ postlink }}">{{ post/title }}</a></h2>
	<p class="meta">Published on {{ post/date '%%Y/%%m/%%d @%%H:%%M:%%S' strftime }} by <b>{{ post/author }}</b></p>
	%if post/thumbnail exists
		<div class="thumbnail-container">
				<a class="more" href="{{ postlink }}">{{ post/thumbnail }}</a>
		</div>
	%end
	<p class="summary">
		{{ post/content truncate }}&nbsp;<a class="more" href="{{ postlink }}">[...Read More]</a>
	</p>
%end


%func makeslides: postpath posts
	<section class="slides">
	%for post: posts
		<div class="slide">
			%call postsummary: postpath post
		</div>
	%end
	</section>
%end

%func postnavigation: postid posts name
	%if posts || 0 ==
		%exit
	%end
		<section class="postnav">
		<div class="postnav-left">
		%if postid 0 >
			%set 'firstpost': posts 0 at
			<a href="{{ firstpost/slug '.html' + //+ }}"><div class="nextpost">&#x300A; Latest {{ name }}</div></a>
			%if postid 1 > 
				%set 'nextpost': posts (postid 1 -) at
				<a href="{{ nextpost/slug '.html' + //+ }}"><div class="nextpost">&#x2329; Next {{ name }}</div></a>
			%end
		%else
			&nbsp;
		%end
		</div>
		<div class="postnav-right">
		%if postid (posts length 1 -) < 
			%if postid (posts length 2 - ) <
				%set 'prevpost': posts (postid 1 +) at
				<a href="{{ prevpost/slug '.html' + //+ }}"><div class="prevpost">Previous {{ name }} &#x232a;</div></a>
			%end
			%set 'lastpost': posts (posts length 1 -) at
			<a href="{{ lastpost/slug '.html' + //+ }}"><div class="prevpost">Oldest {{ name }} &#x300B;</div></a>
		%else
			&nbsp;
		%end
		</div>
		</section>
%end

%func postpage: postid post
	%output 'blog' post/slug '.html' + //+
		%wrap page: post/title ( 'Post: ' post/title +) '..'
			<article>
			%call postnavigation: postid content/sortedposts 'post'
			<h1>{{ post/title }}</h1>
			<p class="meta">Published on {{ post/date "%%d/%%m/%%Y @%%H:%%M:%%S" strftime }} by <b>{{ post/author }}</b></p>
			<section class="mainsection">
			{{ post/content }}
			</section>
			<ul class="posttags">
				%for tag: post/tags
				<li>{{ tag }}</li>
				%end
			</ul>
			%call postnavigation: postid content/sortedposts 'post'
			</article>
		%end
	%end
%end

%# outputs a blog page for each blog post in the blog/ subdirectory
%for postid post: content/sortedposts enumerate
	%call postpage: postid post
%end

%func paginatenavigation: pageid pagecount basename
	%if pagecount 0 ==
		%exit
	%end
		<section class="postnav">
		<div class="postnav-left">
		%if pageid 0 >
			%set 'firstpage': basename '.html' +
			<a href="{{ firstpage }}"><div class="prevpage">&#x300A; First page</div></a>
			%if pageid 1 > 
				%set 'prevpageid': pageid 1 -
				%set 'prevpage': basename prevpageid str '' prevpageid 0 > ? '.html' sum
				<a href="{{ prevpage }}"><div class="prevpage">&#x2329; Previous page</div></a>
			%end
		%else
			&nbsp;
		%end
		</div>
		<div class="postnav-right">
		%if pageid ( pagecount 1 - ) < 
			%if pageid ( pagecount 2 - ) < 
				%set 'nextpageid': pageid 1 + 
				%set 'nextpage': basename nextpageid str '.html' sum
				<a href="{{ nextpage }}"><div class="nextpage">Next page &#x232a;</div></a>
			%end
			%set 'lastpage': basename pagecount 1 - str '.html' sum
			<a href="{{ lastpage }}"><div class="nextpage">Last page &#x300B;</div></a>
		%else
			&nbsp;
		%end
		</div>
		</section>
%end

%- used for blog/index[].html, articles/index[].html, projects/index[].html and sketches/index[].html
%func makeindex: title targetdir posts postsdir description
	%set 'postgroups': posts config/paginatecount groupby
	%set 'pagecount': posts length config/paginatecount /
	%for pageid postgroup: postgroups enumerate
		%output targetdir ( 'index' ( pageid str '' pageid 0 > ? ) '.html' sum ) //+
			%wrap page: config/title title '..'
				<article>
				%call paginatenavigation: pageid pagecount 'index'
				<div class="postnav">
					<h1>{{ title }}</h1>
					<p class="rsslink"><a href="rss.xml">RSS Feed</a></p>
				</div>
				<p>{{ description }}</p>
				%call makeslides: postsdir postgroup
				%call paginatenavigation: pageid pagecount 'index'
				</article>
			%end
		%end
	%end
%end

%call makeindex: 'generated with rezyn' '' content/sortedposts 'blog' content/blog.html/content

%output 'about.html'
	%wrap page: 'About rezyn' '' ''
	{{ content/about.html/content }}
	%end
%end

%output 'contact.html'
	%wrap page: 'Contact g0rb' '' ''
	{{ content/contact.html/content }}
	%end
%end

