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
