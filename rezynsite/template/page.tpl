%----------------------------------------------------------------------
%- This is the main page template
%- All pages on the site will wrap this around them
%----------------------------------------------------------------------

%func page: title subtitle base_path
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }} - {{ subtitle }}</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width">
    <link href="{{ '/' config/tgtsubdir 'favicon.ico' //+ }}" rel="icon" type="image/x-icon">
    <link rel="stylesheet" type="text/css" href="{{ '/' config/tgtsubdir 'css' ('structure-' csskeys/structure '.css' sum) //+ }}">
    <link rel="stylesheet" type="text/css" href="{{ '/' config/tgtsubdir 'css' ('style-'     csskeys/style     '.css' sum) //+ }}">
    <link rel="alternate"  type="application/rss+xml" href="{{ '/' config/tgtsubdir     'rss.xml' //+ }}" title="rezyn feed">
</head>
<body><script>0</script>
<main>
<nav>
<section class="titlesection">
    <a href="{{ '/' config/tgtsubdir //+ }}"><div class="titleimage"><img id="titleimage" src="{{ '/' config/tgtsubdir 'images' 'title.png' //+ }}" /></div></a>
    <div class="sitenavigation">
    <span class="home">
        <a href="{{ '/' config/tgtsubdir                   //+ }}">Home</a>
        <a href="{{ '/' config/tgtsubdir 'contact.html'    //+ }}">Contact</a>
        <a href="{{ '/' config/tgtsubdir 'about.html'      //+ }}">About</a>
    </span>
    </div>
</section>
</nav>

%embed
</main>
<footer>
    <section>
        <p>Content &copy; {{ config/current_year }} g0rb</p>
    </section>
</footer>
</body>
</html>
%end
