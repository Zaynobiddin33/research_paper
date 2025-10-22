document.addEventListener("DOMContentLoaded", () => {
    const copyBtn = document.getElementById("copyCitation");
    const citationText = document.getElementById("citationText");

    if (copyBtn && citationText) {
        copyBtn.addEventListener("click", () => {
            // Create a temporary textarea for copying
            const tempInput = document.createElement("textarea");
            tempInput.value = citationText.value || citationText.textContent;
            document.body.appendChild(tempInput);
            tempInput.select();
            document.execCommand("copy");
            document.body.removeChild(tempInput);

            // Optional feedback
            copyBtn.textContent = "Nusxalandi!";
            setTimeout(() => (copyBtn.textContent = "Nusxalash"), 1500);
        });
    }
});
