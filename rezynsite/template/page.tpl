%func page: title subtitle base_path
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }} - {{ subtitle }}</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width">
    <link href="{{ base_path 'favicon.ico' pathjoin }}" rel="icon" type="image/x-icon">
    <link rel="stylesheet" type="text/css" href="{{ base_path 'css' ('structure-'    csskeys/structure   '.css' sum) //+ }}">
    <link rel="stylesheet" type="text/css" href="{{ base_path 'css' ('style-'        csskeys/style       '.css' sum) //+ }}">
    <link rel="alternate"  type="application/rss+xml" href="{{ base_path             'rss.xml' //+  }}" title="rezyn feed">
</head>
<body><script>0</script>
<main>
<nav>
<section class="titlesection">
    <a href="{{ base_path }}/"><div class="titleimage"><img id="titleimage" src="{{ base_path 'images' 'title.png' //+ }}" /></div></a>
    <div class="sitenavigation">
    <span class="home">
        <a href="{{ base_path '/'               //+ }}">Home</a>
        <a href="{{ base_path 'contact.html'    //+ }}">Contact</a>
        <a href="{{ base_path 'about.html'      //+ }}">About</a>
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
