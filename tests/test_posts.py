def test_public_can_browse_published_posts(client, db_session, test_users):
    from app.models.post import Post
    post = Post(
        title="Public Guide",
        slug="public-guide",
        summary="A public test article",
        content="This is public content.",
        is_published=True,
        author_id=test_users["alice"].id
    )
    db_session.add(post)
    db_session.commit()

    # Request without any auth headers
    response = client.get("/api/v1/posts")
    assert response.status_code == 200
    posts = response.json()
    assert len(posts) == 1
    assert posts[0]["title"] == "Public Guide"


def test_public_cannot_see_unpublished_draft_in_feed(client, db_session, test_users):
    from app.models.post import Post
    draft = Post(
        title="Secret Draft",
        slug="secret-draft",
        content="Draft content not ready for the world.",
        is_published=False,
        author_id=test_users["alice"].id
    )
    db_session.add(draft)
    db_session.commit()

    response = client.get("/api/v1/posts")
    assert response.status_code == 200
    posts = response.json()
    assert len(posts) == 0


def test_public_cannot_read_draft_detail(client, db_session, test_users):
    from app.models.post import Post
    draft = Post(
        title="Secret Draft",
        slug="secret-draft",
        content="Draft content not ready for the world.",
        is_published=False,
        author_id=test_users["alice"].id
    )
    db_session.add(draft)
    db_session.commit()

    # Unauthenticated attempt
    response = client.get(f"/api/v1/posts/{draft.slug}")
    assert response.status_code == 403


def test_author_can_read_own_draft_detail(client, db_session, test_users, alice_headers):
    from app.models.post import Post
    draft = Post(
        title="Secret Draft",
        slug="secret-draft",
        content="Draft content not ready for the world.",
        is_published=False,
        author_id=test_users["alice"].id
    )
    db_session.add(draft)
    db_session.commit()

    response = client.get(f"/api/v1/posts/{draft.slug}", headers=alice_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Secret Draft"


def test_create_post_authenticated(client, alice_headers):
    response = client.post(
        "/api/v1/posts",
        headers=alice_headers,
        json={
            "title": "My Brand New Post",
            "content": "# Heading\n\nThis is the markdown body of the post.",
            "tags": "test,python",
            "is_published": True
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My Brand New Post"
    assert data["slug"] == "my-brand-new-post"
    assert data["author"]["username"] == "alice"


def test_create_post_unauthenticated_fails(client):
    response = client.post(
        "/api/v1/posts",
        json={
            "title": "Unauthorized Post",
            "content": "Should not be created."
        }
    )
    assert response.status_code == 401


def test_user_cannot_edit_another_users_post(client, db_session, test_users, bob_headers):
    from app.models.post import Post
    post = Post(
        title="Alice's Article",
        slug="alices-article",
        content="Original content written by Alice.",
        is_published=True,
        author_id=test_users["alice"].id
    )
    db_session.add(post)
    db_session.commit()

    # Bob tries to edit Alice's post
    response = client.put(
        f"/api/v1/posts/{post.id}",
        headers=bob_headers,
        json={"title": "Hacked Title by Bob"}
    )
    assert response.status_code == 403
    assert "not authorized to edit" in response.json()["detail"].lower()


def test_user_cannot_delete_another_users_post(client, db_session, test_users, bob_headers):
    from app.models.post import Post
    post = Post(
        title="Alice's Post",
        slug="alices-post",
        content="Original content.",
        is_published=True,
        author_id=test_users["alice"].id
    )
    db_session.add(post)
    db_session.commit()

    # Bob tries to delete Alice's post
    response = client.delete(f"/api/v1/posts/{post.id}", headers=bob_headers)
    assert response.status_code == 403


def test_author_can_update_own_post(client, db_session, test_users, alice_headers):
    from app.models.post import Post
    post = Post(
        title="Alice's Post",
        slug="alices-post",
        content="Original content.",
        is_published=True,
        author_id=test_users["alice"].id
    )
    db_session.add(post)
    db_session.commit()

    response = client.put(
        f"/api/v1/posts/{post.id}",
        headers=alice_headers,
        json={"title": "Updated Title by Alice", "content": "Updated body content."}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title by Alice"


def test_author_can_delete_own_post(client, db_session, test_users, alice_headers):
    from app.models.post import Post
    post = Post(
        title="Delete Me",
        slug="delete-me",
        content="To be deleted.",
        is_published=True,
        author_id=test_users["alice"].id
    )
    db_session.add(post)
    db_session.commit()

    response = client.delete(f"/api/v1/posts/{post.id}", headers=alice_headers)
    assert response.status_code == 200
