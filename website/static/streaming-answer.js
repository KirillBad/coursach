const submit_btns = document.querySelectorAll(".submit-btn");
const input = document.querySelector('.question');
const cards_number = document.querySelector('.cards_number');
const answer = document.querySelector('.answer');
const card_container = document.querySelector('.card-container');
const grid_after_answer = document.querySelector('.grid-after-answer');
const new_question = document.querySelector('.new_question');
const balance = document.querySelector('.balance');

submit_btns.forEach(btn =>
    btn.addEventListener("click", async (e) => {
        e.preventDefault();

        submit_btns.forEach(btn => btn.disabled = true);

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
        console.log(json)

        card_container.innerHTML = ``

        if (json.balance) {
            balance.innerText = "Баланс раскладов: " + json.balance
        }

        if (json.cards) {
            json.cards.forEach(card => {
                const cardElement = document.createElement('div');
                cardElement.className = 'card d-none';

                const frontDiv = document.createElement('div');
                frontDiv.className = 'front';
                const frontImg = document.createElement('img');
                frontImg.src = '../static/img/back.webp';
                frontImg.alt = 'Front Image';
                frontDiv.appendChild(frontImg);

                const backDiv = document.createElement('div');
                backDiv.className = 'back';
                const backImg = document.createElement('img');
                backImg.src = `../static/cards/${card.name}.webp`;
                backImg.alt = card.name;

                if (card.reversed) {
                    backImg.style.transform = 'rotate(180deg)';
                }

                backImg.onload = () => {
                    cardElement.classList.remove('d-none');
                };
                backDiv.appendChild(backImg);


                cardElement.appendChild(frontDiv);
                cardElement.appendChild(backDiv);

                card_container.appendChild(cardElement);
            });
        }
        while (true) {
            const { done, value } = await reader.read();
            output += new TextDecoder().decode(value);
            answer.innerHTML = output;

            if (done) {
                grid_after_answer.style.display = 'grid';
                submit_btns.forEach(btn => btn.disabled = false);
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