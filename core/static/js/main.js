document.addEventListener("DOMContentLoaded", () => {
	const toggle = document.querySelector(".nav-toggle");
	const navigation = document.getElementById("primary-navigation");
	if (!toggle || !navigation) return;

	const mobileBreakpoint = 960;

	const syncNavigationState = () => {
		const isMobile = window.innerWidth <= mobileBreakpoint;
		if (isMobile) {
			navigation.setAttribute("aria-hidden", toggle.getAttribute("aria-expanded") === "true" ? "false" : "true");
		} else {
			navigation.removeAttribute("aria-hidden");
			toggle.setAttribute("aria-expanded", "false");
		}
	};

	const toggleNavigation = () => {
		const isExpanded = toggle.getAttribute("aria-expanded") === "true";
		toggle.setAttribute("aria-expanded", String(!isExpanded));
		navigation.setAttribute("aria-hidden", isExpanded ? "true" : "false");
	};

	toggle.addEventListener("click", () => {
		toggleNavigation();
	});

	navigation.querySelectorAll("a").forEach((link) => {
		link.addEventListener("click", () => {
			if (window.innerWidth <= mobileBreakpoint) {
				toggle.setAttribute("aria-expanded", "false");
				navigation.setAttribute("aria-hidden", "true");
			}
		});
	});

	window.addEventListener("resize", () => {
		syncNavigationState();
	});

	document.addEventListener("keyup", (event) => {
		if (event.key === "Escape" && window.innerWidth <= mobileBreakpoint) {
			toggle.setAttribute("aria-expanded", "false");
			navigation.setAttribute("aria-hidden", "true");
		}
	});

	syncNavigationState();
});
