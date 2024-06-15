const submit_btns = document.querySelectorAll(".submit-btn");
const input = document.querySelector('.question');
const cards_number = document.querySelector('.cards_number');
const answer = document.querySelector('.answer');
const card_container = document.querySelector('.card-container');
const grid_after_answer = document.querySelector('.grid-after-answer');
const new_question = document.querySelector('.new_question');

submit_btns.forEach(btn =>
    btn.addEventListener("click", async (e) => {
        e.preventDefault();

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

        grid_after_answer.style.display = 'none';
        answer.innerHTML = ``

        const reader = response.body.getReader();
        let output = "";

        const { done, value } = await reader.read();
        const text = new TextDecoder().decode(value);
        const json = JSON.parse(text);

        card_container.innerHTML = ``

        if (json.cards) {
            json.cards.forEach(card => {
                card_container.innerHTML += `
                    <div class="card">
                        <div class="front">
                            <img src="../static/img/back.webp" alt="Front Image">
                        </div>
                        <div class="back">
                            <img src="../static/cards/${card}.webp" alt="${card}">
                        </div>
                    </div>
                `;
            });
        }

        while (true) {
            const { done, value } = await reader.read();
            output += new TextDecoder().decode(value);
            answer.innerHTML = output;

            if (done) {
                grid_after_answer.style.display = 'grid';
                return;
            }
        }
    })
)

new_question.addEventListener('click', (e) => {
  input.value = '';
  input.focus();
  window.scrollTo({ top: 0, behavior: 'smooth' });
})