document.querySelectorAll("[data-password-toggle]").forEach((button) => {
	button.addEventListener("click", () => {
		const passwordInput = document.getElementById(button.getAttribute("aria-controls"));
		if (!passwordInput) return;

		const isVisible = passwordInput.type === "password";
		passwordInput.type = isVisible ? "text" : "password";
		button.textContent = isVisible ? "Hide" : "Show";
		button.setAttribute("aria-pressed", String(isVisible));
	});
});

const registrationPassword = document.querySelector("#registration-form #password");
const strengthBars = document.querySelectorAll("[data-strength-bar]");
const strengthLabel = document.querySelector("#password-guidance");

if (registrationPassword && strengthLabel) {
	registrationPassword.addEventListener("input", () => {
		const password = registrationPassword.value;
		const checks = [
			password.length >= 8,
			/[a-z]/.test(password),
			/[A-Z]/.test(password),
			/[0-9]/.test(password),
			/[^a-zA-Z0-9]/.test(password),
		];
		const score = checks.filter(Boolean).length;
		const strength = score < 4 ? "weak" : score < 5 ? "good" : "strong";

		strengthBars.forEach((bar, index) => {
			bar.className = index < score ? `is-${strength}` : "";
		});
		strengthLabel.textContent = password
			? `Password strength: ${strength}`
			: "Use at least 8 characters and 3 character types.";
	});
}

document.querySelectorAll("[data-social-provider]").forEach((button) => {
	button.addEventListener("click", () => {
		const status = button.closest(".form-wrap").querySelector("[data-social-status]");
		status.textContent = `${button.dataset.socialProvider} sign-in is not configured yet. Use your school email instead.`;
		button.classList.remove("social-pulse");
		void button.offsetWidth;
		button.classList.add("social-pulse");
	});
});

const sidebar = document.querySelector("#dashboard-sidebar");
const sidebarToggle = document.querySelector("[data-sidebar-toggle]");
const sidebarClose = document.querySelector("[data-sidebar-close]");

if (sidebar && sidebarToggle && sidebarClose) {
	const closeSidebar = () => {
		document.body.classList.remove("sidebar-open");
		sidebarToggle.setAttribute("aria-expanded", "false");
		sidebarToggle.setAttribute("aria-label", "Open navigation");
	};

	const closeDropdowns = (exceptGroup) => {
		sidebar.querySelectorAll(".sidebar-group.is-open").forEach((group) => {
			if (group === exceptGroup) return;
			group.classList.remove("is-open");
			group.querySelector(".sidebar-group-toggle")?.setAttribute("aria-expanded", "false");
		});
	};

	sidebarToggle.addEventListener("click", () => {
		const isOpen = document.body.classList.toggle("sidebar-open");
		sidebarToggle.setAttribute("aria-expanded", String(isOpen));
		sidebarToggle.setAttribute("aria-label", isOpen ? "Close navigation" : "Open navigation");
	});

	sidebarClose.addEventListener("click", closeSidebar);

	sidebar.querySelectorAll(".sidebar-group-toggle").forEach((button) => {
		button.addEventListener("click", () => {
			const group = button.closest(".sidebar-group");
			if (!group) return;
			const willOpen = !group.classList.contains("is-open");
			closeDropdowns(group);
			group.classList.toggle("is-open", willOpen);
			button.setAttribute("aria-expanded", String(willOpen));
		});
	});

	sidebar.querySelectorAll("[data-sidebar-home]").forEach((link) => {
		link.addEventListener("click", () => {
			closeSidebar();
		});
	});

	document.addEventListener("keydown", (event) => {
		if (event.key !== "Escape") return;
		const hasOpenDropdown = sidebar.querySelector(".sidebar-group.is-open");
		if (hasOpenDropdown) {
			closeDropdowns();
			return;
		}
		if (!document.body.classList.contains("sidebar-open")) return;
		closeSidebar();
		sidebarToggle.focus();
	});

	window.matchMedia("(min-width: 761px)").addEventListener("change", (event) => {
		if (event.matches) closeSidebar();
	});
}
