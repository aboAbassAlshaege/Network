class PostEditor {
    constructor(button) {
        this.button = button;  // The edit button
        this.post = this.button.closest(".post");  // The parent post element
        this.text_paragraph = this.post.querySelector("p");  // Paragraph with post content
        this.date_stamp = this.post.querySelector("small"); // The date small element
        this.post_id = this.post.getAttribute("data-post-id");  // Post ID
        this.csrfToken = csrfToken;  // CSRF token
        this.isEditing = false;
        this.init();  // Initialize event handlers
    }

    init() {
        this.button.addEventListener("click", () => this.toggleEdit())
    }

    toggleEdit() {
        // If the button says "Edit", change it to "Save" and make content editable
        if (this.isEditing) {
            this.handleSave()
        } else {
            this.editPost()
        }
    }

    editPost() {
        // Create a textarea to replace the post content
        this.inputTextArea = document.createElement("textarea");
        this.inputTextArea.value = this.text_paragraph.textContent.trim();  // Use textContent for plain text

        // Replace paragraph with textarea
        this.text_paragraph.textContent = "";
        this.text_paragraph.appendChild(this.inputTextArea);

        // Change the button text to "Save"
        this.button.innerText = "Save";

        this.isEditing = true
    }

    handleSave() {
        const updated_content = this.inputTextArea.value.trim();
        if (!updated_content) {
            alert("Content cannot be empty");
            return;
        }
        const formData = new FormData();
        formData.append("updated_content", updated_content);
        formData.append("csrfmiddlewaretoken", this.csrfToken);
        formData.append("post_id", this.post_id);
        // Send the updated content to the server
        fetch(update_post_url, {
            method: "POST",
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert("Error: " + data.error);
                } else {
                    // Update the post with the new content
                    this.text_paragraph.textContent = data.post.updated_content;
                    // Change the button back to "Edit"
                    this.button.innerText = "Edit";
                    // Change the date stamp
                    this.date_stamp.innerHTML = data.post.date_stamp;
                    //
                    this.isEditing = false;
                }
            })
            .catch(error => alert("catch error: " + error));
    }
}
document.querySelectorAll(".edit-btn").forEach(button => {
    new PostEditor(button);
}
)