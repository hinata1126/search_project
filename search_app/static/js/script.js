document.addEventListener("DOMContentLoaded", function() {
    const stars = document.querySelectorAll('.star-rating label');

    stars.forEach(function(star) {
        // ホバー時の処理
        star.addEventListener('mouseover', function() {
            const ratingValue = parseInt(star.getAttribute('for').replace('rating', ''));

            stars.forEach(function(starLabel) {
                const starValue = parseInt(starLabel.getAttribute('for').replace('rating', ''));
                // ホバーされた星以下の星を金色に
                starLabel.style.color = starValue <= ratingValue ? 'gold' : 'gray';
            });
        });

        // ホバー外れた時の処理
        star.addEventListener('mouseout', function() {
            stars.forEach(function(starLabel) {
                starLabel.style.color = '';  // 元の色に戻す
            });
        });
    });
});
