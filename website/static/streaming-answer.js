const submit_btns = document.querySelectorAll(".submit-btn");
const input = document.querySelector('.question');
const cards_number = document.querySelector('.cards_number');
const answer = document.querySelector('.answer');
const card_container = document.querySelector('.card-container');
const grid_after_answer = document.querySelector('.grid-after-answer');
const new_question = document.querySelector('.new_question');

submit_btns.forEach(btn => {
    btn.addEventListener("click", async (e) => {
        e.preventDefault();

        grid_after_answer.style.display = 'none';
        answer.innerHTML = ``;
        card_container.innerHTML = ``;

        const response = await fetch("/answer", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({message: input.value, cards_number: cards_number.value})
        });

        if (response.status === 400) {
            const result = await response.json();
            const flashContainer = document.createElement('div');
            flashContainer.classList.add('popup');
            flashContainer.innerHTML = `
                <img src="../static/img/cross.webp" alt="popup-cross">
                <p>${result.message}</p>
                <button class="popup-close">Хорошо</button>
            `;
            document.body.appendChild(flashContainer);

            setTimeout(() => {
                flashContainer.classList.add('open-popup');
            }, 1);

            flashContainer.querySelector('.popup-close').addEventListener('click', function() {
                flashContainer.classList.remove('open-popup');
            });
            return;
        }

        const reader = response.body.getReader();
        let output = "";

        const { done, value } = await reader.read();
        const text = new TextDecoder().decode(value);
        const json = JSON.parse(text);

        if (json.cards) {
            await preloadImages(json.cards); // Preload images before displaying them
            json.cards.forEach(card => {
                const cardElement = document.createElement('div');
                cardElement.classList.add('card');
                cardElement.innerHTML = `
                    <div class="front">
                        <img src="../static/img/back.webp" alt="Front Image">
                    </div>
                    <div class="back">
                        <img src="../static/cards/${card}.webp" alt="${card}">
                    </div>
                `;
                card_container.appendChild(cardElement);
            });
        }

        // Trigger animations only after all cards are added to the DOM
        triggerCardAnimations();

        while (true) {
            const { done, value } = await reader.read();
            output += new TextDecoder().decode(value);
            answer.innerHTML = output;

            if (done) {
                grid_after_answer.style.display = 'grid';
                return;
            }
        }
    });
});

new_question.addEventListener('click', (e) => {
    input.value = '';
    input.focus();
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

async function preloadImages(cards) {
    const imagePromises = cards.map(card => {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.src = `../static/cards/${card}.webp`;
            img.onload = resolve;
            img.onerror = reject;
        });
    });
    await Promise.all(imagePromises);
}

function triggerCardAnimations() {
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        // Add a class to trigger CSS animations
        card.classList.add('animate-card');
    });
}
