// main/static/main/js/avatar_preview.js

document.addEventListener("DOMContentLoaded", function () {
    const avatarInput = document.getElementById("avatarInput");
    const avatarPreview = document.getElementById("avatarPreview");

    if (!avatarInput || !avatarPreview) return;

    avatarInput.addEventListener("change", function () {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                avatarPreview.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });
});

// main/static/main/js/register_validation.js

document.addEventListener("DOMContentLoaded", function () {
    // --- Username availability check ---
    const usernameInput = document.querySelector('input[name="username"]');
    if (usernameInput) {
        const usernameMsgBox = document.createElement("div");
        usernameMsgBox.className =
            "hidden mt-2 p-2 rounded-lg text-sm font-medium transition-all duration-200";
        usernameInput.insertAdjacentElement("afterend", usernameMsgBox);

        usernameInput.addEventListener("input", async () => {
            const username = usernameInput.value.trim();

            if (username.length < 3) {
                usernameMsgBox.textContent =
                    "Foydalanuvchi nomi juda qisqa (kamida 3ta belgi).";
                usernameMsgBox.className =
                    "mt-2 p-2 rounded-lg bg-yellow-100 text-yellow-700 text-sm font-medium";
                return;
            }

            try {
                const response = await fetch(`/check-username/?username=${username}`);
                const data = await response.json();

                if (data.exists) {
                    usernameMsgBox.textContent = "Bu foydalanuvchi nomi allaqachon mavjud.";
                    usernameMsgBox.className =
                        "mt-2 p-2 rounded-lg bg-red-100 text-red-700 text-sm font-medium";
                } else {
                    usernameMsgBox.textContent = "Bu foydalanuvchi nomi bo'sh!";
                    usernameMsgBox.className =
                        "mt-2 p-2 rounded-lg bg-green-100 text-green-700 text-sm font-medium";
                }
            } catch (error) {
                usernameMsgBox.textContent =
                    "Xatolik yuz berdi. Iltimos, qayta urinib ko‘ring.";
                usernameMsgBox.className =
                    "mt-2 p-2 rounded-lg bg-red-100 text-red-700 text-sm font-medium";
            }
        });
    }

    // --- Password matching check ---
    const passwordInput = document.querySelector('input[name="password"]');
    const checkPasswordInput = document.querySelector('input[name="check_password"]');
    if (passwordInput && checkPasswordInput) {
        const passwordMsgBox = document.createElement("div");
        passwordMsgBox.className =
            "hidden mt-2 p-2 rounded-lg text-sm font-medium transition-all duration-200";
        checkPasswordInput.insertAdjacentElement("afterend", passwordMsgBox);

        function validatePasswords() {
            if (checkPasswordInput.value === "") {
                passwordMsgBox.classList.add("hidden");
                return;
            }

            passwordMsgBox.classList.remove("hidden");
            if (passwordInput.value === checkPasswordInput.value) {
                passwordMsgBox.textContent = "Parollar mos.";
                passwordMsgBox.className =
                    "mt-2 p-2 rounded-lg bg-green-100 text-green-700 text-sm font-medium";
            } else {
                passwordMsgBox.textContent = "Parollar mos emas.";
                passwordMsgBox.className =
                    "mt-2 p-2 rounded-lg bg-red-100 text-red-700 text-sm font-medium";
            }
        }

        passwordInput.addEventListener("input", validatePasswords);
        checkPasswordInput.addEventListener("input", validatePasswords);
    }
});
