async function checkId() {
    const username = document.getElementById('username').value;
    const msg = document.getElementById('id-msg');
    const submitBtn = document.getElementById('submit-btn');

    if (!username) {
        msg.textContent = '아이디를 입력해주세요.';
        msg.className = 'error';
        return;
    }

    try {
        const response = await fetch('/check-id', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username })
        });
        const data = await response.json();

        if (data.available) {
            msg.textContent = '사용 가능한 아이디입니다.';
            msg.className = 'success';
            msg.dataset.valid = "true";
        } else {
            msg.textContent = '이미 사용 중인 아이디입니다.';
            msg.className = 'error';
            msg.dataset.valid = "false";
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

function validateForm() {
    const pw = document.getElementById('password').value;
    const pwConfirm = document.getElementById('password_confirm').value;
    const idValid = document.getElementById('id-msg').dataset.valid;

    if (idValid !== "true") {
        alert('아이디 중복 점검을 완료해주세요.');
        return false;
    }

    if (pw !== pwConfirm) {
        alert('비밀번호가 일치하지 않습니다.');
        return false;
    }

    return true;
}
