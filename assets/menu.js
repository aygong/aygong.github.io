(function () {
  var currentScript = document.currentScript;
  var current = currentScript.getAttribute("data-current");
  var root = new URL("../", new URL(".", currentScript.src));

  function href(path) {
    return new URL(path, root).href;
  }

  function item(path, label, key, extra) {
    var className = current === key ? ' class="current"' : "";
    var attrs = extra ? " " + extra : "";
    return '<div class="menu-item"><a href="' + href(path) + '"' + className + attrs + ">" + label + "</a></div>";
  }

  document.write(
    '<td id="layout-menu">' +
      '<div class="menu-category">Home</div>' +
      item("index.html", "About&nbsp;Me", "home") +
      item("service.html", "Services", "services") +
      item("docu/resume.pdf", "CV", "", 'target="_blank"') +
      '<div class="menu-category">Research</div>' +
      item("pub.html", "Publications", "publications") +
      item("project.html", "Projects", "projects") +
      '<div class="menu-category">Moments</div>' +
      item("post.html", "Posts", "posts") +
      item("photo.html", "Photos", "photos") +
    "</td>"
  );
})();
