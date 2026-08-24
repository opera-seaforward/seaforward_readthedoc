document.addEventListener("DOMContentLoaded", function () {
  var copyIcon = `
    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <rect x="9" y="9" width="13" height="13" rx="2"></rect>
      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
    </svg>`;

  var checkIcon = `
    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="20 6 9 17 4 12"></polyline>
    </svg>`;

  document.querySelectorAll(".highlight").forEach(function (block) {
    var pre = block.querySelector("pre");
    if (!pre) return;

    var button = document.createElement("button");
    button.className = "copy-code-button";
    button.type = "button";
    button.setAttribute("aria-label", "Copier le code");
    button.title = "Copier le code";
    button.innerHTML = copyIcon;

    button.addEventListener("click", function () {
      navigator.clipboard.writeText(pre.innerText).then(function () {
        button.innerHTML = checkIcon;
        button.classList.add("copied");
        setTimeout(function () {
          button.innerHTML = copyIcon;
          button.classList.remove("copied");
        }, 2000);
      });
    });

    // On attache toujours le bouton au conteneur principal (.highlight) 
    // pour éviter qu'il ne soit masqué si on cache le .filename via CSS.
    block.style.position = "relative";
    block.appendChild(button);
  });
});