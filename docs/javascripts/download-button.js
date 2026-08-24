document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("a[data-download-url]").forEach(function (link) {
    link.addEventListener("click", function (event) {
      var url = link.getAttribute("data-download-url");
      var filename = link.getAttribute("data-download-filename") || "download.ipynb";

      if (!url) return;

      event.preventDefault();

      fetch(url, { mode: "cors" })
        .then(function (response) {
          if (!response.ok) {
            throw new Error("Failed to fetch download");
          }
          return response.blob();
        })
        .then(function (blob) {
          var downloadBlob = blob.type ? blob : new Blob([blob], { type: "application/octet-stream" });
          var objectUrl = window.URL.createObjectURL(downloadBlob);
          var anchor = document.createElement("a");
          anchor.href = objectUrl;
          anchor.download = filename;
          anchor.style.display = "none";
          document.body.appendChild(anchor);
          anchor.click();
          window.setTimeout(function () {
            window.URL.revokeObjectURL(objectUrl);
            anchor.remove();
          }, 1000);
        })
        .catch(function () {
          window.location.href = url;
        });
    });
  });
});