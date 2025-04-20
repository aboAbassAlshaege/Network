class LikeToggle {
    constructor(button) {
        this.button = button; // the like button
        this.post = button.closest(".post");
        this.target_post_id = this.post.dataset.postId;
        this.init();
    }

    init() {
        this.button.addEventListener("click", _ => this.toggle())
    }
    toggle() {
        let formData = new FormData();
        formData.append("csrfmiddlewaretoken", csrfToken);
        formData.append("target_post_id", this.target_post_id);
        fetch(toggle_like_url, {
            method: "POST",
            body: formData
        }).then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(error);
                } else if (data.redirect) {
                    window.location.href = data.redirect;
                } else {
                    alert(data.message);
                    if (data.liked) {
                        this.button.textContent = "Liked"
                    } else {
                        this.button.textContent = "Like"
                    }
                    this.post.querySelector(".total_likes").innerHTML = `Likes: ${data.total_likes}`;
                }
            }).catch(error => { alert(`error from catch: ${error}`) })
    }
}
document.querySelectorAll(".like-btn").forEach(button => {
    new LikeToggle(button)
})