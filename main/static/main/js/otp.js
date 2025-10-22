// main/static/main/js/otp.js

document.addEventListener("DOMContentLoaded", function () {
    const inputs = Array.from(document.querySelectorAll(".otp-digit"));
    const otpHidden = document.getElementById("otpHidden");
    const verifyBtn = document.getElementById("verifyBtn");
    const errorMsg = document.getElementById("errorMsg");
    const resendBtn = document.getElementById("resendBtn");
    const timerText = document.getElementById("timerText");
    const timerElem = document.getElementById("timer");

    if (!inputs.length || !otpHidden) return; // Exit if page doesn't have OTP form

    inputs[0].focus();

    function updateHiddenAndState() {
        const code = inputs.map(i => i.value.trim()).join("");
        otpHidden.value = code;
        verifyBtn.disabled = code.length !== inputs.length || !/^\d{8}$/.test(code);
    }

    function handlePaste(e) {
        e.preventDefault();
        const paste = (e.clipboardData || window.clipboardData).getData("text") || "";
        const digits = paste.replace(/\D/g, "").slice(0, inputs.length).split("");
        if (digits.length === 0) return;
        inputs.forEach((input, i) => (input.value = digits[i] || ""));
        const nextIndex = digits.length >= inputs.length ? inputs.length - 1 : digits.length;
        inputs[nextIndex].focus();
        updateHiddenAndState();
    }

    inputs.forEach((input, idx) => {
        input.addEventListener("input", e => {
            const val = e.target.value;
            if (!/^\d$/.test(val)) {
                e.target.value = val.replace(/\D/g, "").slice(0, 1);
            }
            if (e.target.value && idx < inputs.length - 1) {
                inputs[idx + 1].focus();
                inputs[idx + 1].select();
            }
            updateHiddenAndState();
        });

        input.addEventListener("keydown", e => {
            if (e.key === "Backspace" && !input.value && idx > 0) {
                inputs[idx - 1].focus();
                inputs[idx - 1].select();
            } else if (e.key === "ArrowLeft" && idx > 0) {
                inputs[idx - 1].focus();
            } else if (e.key === "ArrowRight" && idx < inputs.length - 1) {
                inputs[idx + 1].focus();
            }
        });

        input.addEventListener("paste", handlePaste);
    });

    document.getElementById("otpForm").addEventListener("submit", function (e) {
        if (!/^\d{8}$/.test(otpHidden.value.trim())) {
            e.preventDefault();
            errorMsg.textContent = "Please enter the 8-digit code.";
            errorMsg.style.display = "block";
        }
    });

    let countdown = 30;
    let interval = setInterval(updateTimer, 1000);

    function updateTimer() {
        countdown--;
        const mm = String(Math.floor(countdown / 60)).padStart(2, "0");
        const ss = String(countdown % 60).padStart(2, "0");
        timerElem.textContent = `${mm}:${ss}`;
        if (countdown <= 0) {
            clearInterval(interval);
            resendBtn.disabled = false;
            timerText.textContent = "You can resend the code now.";
        }
    }

    resendBtn.addEventListener("click", () => {
        resendBtn.disabled = true;
        countdown = 30;
        timerElem.textContent = "00:30";
        timerText.textContent = "Resend available in";
        interval = setInterval(updateTimer, 1000);
    });
});
