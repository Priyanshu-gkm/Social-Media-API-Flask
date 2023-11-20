<div align="center">
<h1 align="center">
<img src="https://raw.githubusercontent.com/PKief/vscode-material-icon-theme/ec559a9f6bfd399b82bb44393651661b08aaf7ba/icons/folder-markdown-open.svg" width="100" />
<br>SOCIAL_MEDIA_APPLICATION</h1>
<h3>◦ ► Priyanshu Arora - GKM IT</h3>
<h3>◦ Developed with the software and tools below.</h3>

<p align="center">
<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat-square&logo=Python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/flask-logo?style=flat-square&logo=Flask&logoColor=white" alt="Flask" />

</p>
</div>

---

## 📖 Table of Contents

- [📖 Table of Contents](#-table-of-contents)
- [📍 Overview](#-overview)
- [📦 Features](#-features)
- [📂 repository Structure](#-repository-structure)
- [⚙️ Modules](#modules)
- [🚀 Getting Started](#-getting-started)

  - [🔧 Installation](#-installation)
  - [🤖 Running social_media_application](#-running-social_media_application)

- [🤝 Contributing](#-contributing)

---

## 📍 Overview

► **Created a Flask-based REST API that simulates a social media platform where users can post various types of content, including text, image-text, and video-text. Users will also be able to connect with each other and see the posted content. The API will provide endpoints for managing user profiles, connections, and content creation and consumption.**

---

## 📦 Features

►1. User Management:

- User Registration: Users can create new accounts by providing essential information such as username, email, and password.

* User Authentication: Implement user authentication to secure user data and restrict certain operations to authenticated users.
* User Profile: Users can update their profiles, including profile pictures, bio, and other optional details.

2. Social Connections:(like linkedin connections)

   - Follow System: Users can follow or connect with other users, allowing them to see posts from those they follow in their feeds.
   - Unfollow: Users can unfollow other users to stop receiving their posts in their feed.
   - Followers/Following Lists: Users can see a list of their followers and users they are following.

3. Content Creation:

   - Text Posts: Users can create text-only posts with a title and content.
   - Image-Text Posts: Users can create posts with images and associated text.
   - Video-Text Posts: Users can create posts with video content (with streaming support) and associated text.

4. Content Feeds:

   - User Feed: Users have a personalized feed showing posts from users they follow.

5. Search Functionality:

   - Users can search for other users, specific posts, or topics of interest via tags.

6. Notifications:

   - Users receive notifications for new followers, likes, comments, and mentions.

---

## 📂 Repository Structure

```sh
└── social_media_application/
    ├── helpers/
    │   └── permissions.py
    ├── models/
    │   ├── connection.py
    │   ├── notification.py
    │   ├── post.py
    │   ├── post_type.py
    │   ├── profile.py
    │   ├── token.py
    │   └── user.py
    ├── serializers/
    │   ├── connection.py
    │   ├── notification.py
    │   ├── post.py
    │   ├── post_type.py
    │   ├── profile.py
    │   └── user.py
    └── views/
        ├── auth.py
        ├── connection.py
        ├── feed.py
        ├── follow_request.py
        ├── notification.py
        ├── post.py
        ├── post_type.py
        ├── search.py
        └── user.py

```

---

## ⚙️ Modules

<details closed><summary>Models</summary>

| File                      |
| ------------------------- |
| [post.py]({file})         |
| [user.py]({file})         |
| [token.py]({file})        |
| [notification.py]({file}) |
| [profile.py]({file})      |
| [connection.py]({file})   |
| [post_type.py]({file})    |

</details>

<details closed><summary>Serializers</summary>

| File                      |
| ------------------------- |
| [post.py]({file})         |
| [user.py]({file})         |
| [notification.py]({file}) |
| [profile.py]({file})      |
| [connection.py]({file})   |
| [post_type.py]({file})    |

</details>

<details closed><summary>Views</summary>

| File                        |
| --------------------------- |
| [auth.py]({file})           |
| [post.py]({file})           |
| [user.py]({file})           |
| [follow_request.py]({file}) |
| [notification.py]({file})   |
| [feed.py]({file})           |
| [connection.py]({file})     |
| [post_type.py]({file})      |
| [search.py]({file})         |

</details>

<details closed><summary>Helpers</summary>

| File                     | Summary                                                     |
| ------------------------ | ----------------------------------------------------------- |
| [permissions.py]({file}) | ► various permissions used in the project are defined here. |

</details>

---

## 🚀 Getting Started

**_Dependencies_**

Please ensure you have the following dependencies installed on your system:

`- ℹ️ python 3.11.5`

`- ℹ️ flask 3`

### 🔧 Installation

1. Clone the social_media_application repository:

```sh
git clone https://github.com/Priyanshu-gkm/Social-Media-API-Flask.git
```

2. Change to the project directory:

```sh
cd social_media_application
```

3. Install the dependencies:

```sh
pip install -r requirements.txt
```

### 🤖 Running social_media_application

```sh
python app.py
```

## 🤝 Contributing

Contributions are welcome! Here are several ways you can contribute:

- **[Submit Pull Requests](https://github.com/local/social_media_application/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.
- **[Join the Discussions](https://github.com/local/social_media_application/discussions)**: Share your insights, provide feedback, or ask questions.
- **[Report Issues](https://github.com/local/social_media_application/issues)**: Submit bugs found or log feature requests for LOCAL.
