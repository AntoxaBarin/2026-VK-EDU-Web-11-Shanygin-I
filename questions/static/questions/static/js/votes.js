(function () {
    const csrfToken = document.cookie.match(/csrftoken=([^;]+)/)?.[1] ?? '';

    async function postJson(url, body) {
        const resp = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify(body),
        });
        if (!resp.ok) throw new Error(resp.statusText);
        return resp.json();
    }

    function applyVote(widget, vote) {
        const upBtn = widget.querySelector('.vote-up');
        const downBtn = widget.querySelector('.vote-down');
        widget.dataset.userVote = vote;
        if (vote === 1) {
            upBtn.classList.replace('btn-outline-success', 'btn-success');
            downBtn.classList.replace('btn-danger', 'btn-outline-danger');
        } else if (vote === -1) {
            downBtn.classList.replace('btn-outline-danger', 'btn-danger');
            upBtn.classList.replace('btn-success', 'btn-outline-success');
        } else {
            upBtn.classList.replace('btn-success', 'btn-outline-success');
            downBtn.classList.replace('btn-danger', 'btn-outline-danger');
        }
    }

    document.querySelectorAll('.vote-widget[data-url]').forEach(widget => {
        const upBtn = widget.querySelector('.vote-up');
        const downBtn = widget.querySelector('.vote-down');
        const countEl = widget.querySelector('.vote-count');
        const url = widget.dataset.url;

        async function handleVote(value) {
            try {
                const data = await postJson(url, {value});
                countEl.textContent = data.votes;
                applyVote(widget, data.user_vote);
            } catch (e) {
                console.error('Vote failed', e);
            }
        }

        if (upBtn) upBtn.addEventListener('click', () => handleVote(1));
        if (downBtn) downBtn.addEventListener('click', () => handleVote(-1));
    });

    document.querySelectorAll('.mark-correct-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const url = btn.dataset.url;
            const answerId = btn.dataset.answerId;
            try {
                const data = await postJson(url, {});
                const card = document.getElementById('answer-' + answerId);
                if (data.is_correct) {
                    btn.textContent = '✓ Correct Answer';
                    btn.classList.replace('btn-outline-secondary', 'btn-success');
                    card.classList.add('border-success');
                } else {
                    btn.textContent = 'Mark as Correct';
                    btn.classList.replace('btn-success', 'btn-outline-secondary');
                    card.classList.remove('border-success');
                }
            } catch (e) {
                console.error('Mark correct failed', e);
            }
        });
    });
})();
