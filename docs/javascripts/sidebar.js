// docs/javascripts/sidebar.js

var SEA_FORWARD_SIDEBAR_STORAGE_KEY = "sea-forward-sidebar-open";
var SEA_FORWARD_MOBILE_QUERY = "(max-width: 992px)";

function isMobileSidebar() {
    return window.matchMedia(SEA_FORWARD_MOBILE_QUERY).matches;
}

function createSidebarControls() {
    if (document.querySelector(".sidebar-toggle-button")) return;

    var button = document.createElement("button");
    button.type = "button";
    button.className = "sidebar-toggle-button";
    button.setAttribute("aria-label", "Afficher ou masquer le menu");
    button.setAttribute("aria-controls", "sidebar-navigation");
    button.setAttribute("aria-expanded", "false");
    var menuSvg = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>';
    var closeSvg = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>';

    button.innerHTML = '<span class="sidebar-toggle-icon" aria-hidden="true">' + menuSvg + '</span><span class="sidebar-toggle-text">Menu</span>';

    var backdrop = document.createElement("div");
    backdrop.className = "sidebar-backdrop";
    backdrop.setAttribute("aria-hidden", "true");

    document.body.appendChild(backdrop);
    document.body.appendChild(button);

    function syncButtonState() {
        var isOpen = document.body.classList.contains("sidebar-open");
        button.setAttribute("aria-expanded", String(isOpen));
        button.classList.toggle("is-open", isOpen);
        
        var iconSpan = button.querySelector(".sidebar-toggle-icon");
        if (iconSpan) {
            iconSpan.innerHTML = isOpen ? closeSvg : menuSvg;
        }
        
        var textSpan = button.querySelector(".sidebar-toggle-text");
        if (textSpan) {
            textSpan.textContent = isOpen ? "Close" : "Menu";
        }
    }

    function setOpen(open) {
        document.body.classList.toggle("sidebar-open", open);
        try {
            window.localStorage.setItem(SEA_FORWARD_SIDEBAR_STORAGE_KEY, open ? "1" : "0");
        } catch (error) {
            // Ignore storage failures and keep the interaction working.
        }
        syncButtonState();
    }

    button.addEventListener("click", function () {
        setOpen(!document.body.classList.contains("sidebar-open"));
    });

    backdrop.addEventListener("click", function () {
        setOpen(false);
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            setOpen(false);
        }
    });

    document.querySelectorAll(".wy-menu-vertical a[href]").forEach(function (link) {
        link.addEventListener("click", function () {
            if (isMobileSidebar()) {
                setOpen(false);
            }
        });
    });

    function syncFromViewport() {
        if (isMobileSidebar()) {
            var storedState = null;
            try {
                storedState = window.localStorage.getItem(SEA_FORWARD_SIDEBAR_STORAGE_KEY);
            } catch (error) {
                storedState = null;
            }

            document.body.classList.toggle("sidebar-open", storedState === "1");
        } else {
            document.body.classList.remove("sidebar-open");
        }

        syncButtonState();
    }

    syncFromViewport();
    window.addEventListener("resize", syncFromViewport);
    window.addEventListener("orientationchange", syncFromViewport);
}

function initSidebar() {
    if (window.__seaForwardSidebarInitialized) return;
    window.__seaForwardSidebarInitialized = true;

    // 1. Groupes de navigation (Phases comme Setup)
    var captions = document.querySelectorAll(".wy-menu-vertical .caption");
    
    captions.forEach(function (caption) {
        var parentLi = caption.closest("li");
        if (!parentLi) return;
        
        var nextLi = parentLi.nextElementSibling;
        if (!nextLi || nextLi.tagName.toLowerCase() !== "li") return;
        
        nextLi.classList.add("nav-collapsible-container");
        caption.style.cursor = "pointer";
        caption.classList.add("is-collapsible");
        
        caption.addEventListener("click", function(e) {
            e.preventDefault();
            e.stopImmediatePropagation();
            
            var wasOpen = nextLi.classList.contains("js-open");
            
            // Fermer toutes les autres phases
            captions.forEach(function(c) {
                c.classList.remove("js-open");
                var p = c.closest("li");
                if (p && p.nextElementSibling) {
                    p.nextElementSibling.classList.remove("js-open");
                }
            });
            
            if (!wasOpen) {
                nextLi.classList.add("js-open");
                caption.classList.add("js-open");
            }
        });
        
        // Ouvrir UNIQUEMENT si la page active s'y trouve réellement (on exclut les ul.current du thème)
        var hasActivePage = false;
        if (nextLi.classList.contains("current")) hasActivePage = true;
        if (nextLi.querySelector("li.current, a.current")) hasActivePage = true;
        
        if (hasActivePage) {
            nextLi.classList.add("js-open");
            caption.classList.add("js-open");
        }
    });

    // 2. Sous-menus internes (with-children)
    var parents = document.querySelectorAll(".wy-menu-vertical li.with-children");
    parents.forEach(function (parentLi) {
        var link = parentLi.querySelector("a");
        var nextLi = parentLi.nextElementSibling;
        
        if (!nextLi || nextLi.tagName.toLowerCase() !== "li") return;
        
        nextLi.classList.add("nav-collapsible-container");
        
        var target = link ? link : parentLi;
        target.addEventListener("click", function(e) {
            if (link && (!link.getAttribute("href") || link.getAttribute("href") === "#" || link.getAttribute("href").startsWith("#"))) {
                e.preventDefault();
            }
            e.stopImmediatePropagation();
            
            var wasOpen = nextLi.classList.contains("js-open");
            
            if (wasOpen) {
                nextLi.classList.remove("js-open");
                parentLi.classList.remove("js-open");
            } else {
                nextLi.classList.add("js-open");
                parentLi.classList.add("js-open");
            }
        });
        
        // Ouvrir UNIQUEMENT si la page active s'y trouve réellement
        var hasActivePage = false;
        if (nextLi.classList.contains("current") || parentLi.classList.contains("current")) hasActivePage = true;
        if (nextLi.querySelector("li.current, a.current")) hasActivePage = true;
        
        if (hasActivePage) {
            nextLi.classList.add("js-open");
            parentLi.classList.add("js-open");
        }
    });

    createSidebarControls();
}

// Lancer dès que possible, et aussi au DOMContentLoaded pour être sûr
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initSidebar);
} else {
    initSidebar();
}
