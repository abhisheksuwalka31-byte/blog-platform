from app.models.post import Post


def test_toggle_like_flow(client, db_session, test_users, bob_headers):
    post = Post(
        title="Post for Liking",
        slug="post-for-liking",
        content="Content for like testing.",
        is_published=True,
        author_id=test_users["alice"].id
    )
    db_session.add(post)
    db_session.commit()

    # 1. Unauthenticated like attempt -> 401
    resp_unauth = client.post(f"/api/v1/posts/{post.id}/like")
    assert resp_unauth.status_code == 401

    # 2. Bob likes post -> liked: True, likes_count: 1
    resp_like = client.post(f"/api/v1/posts/{post.id}/like", headers=bob_headers)
    assert resp_like.status_code == 200
    data_like = resp_like.json()
    assert data_like["liked"] is True
    assert data_like["likes_count"] == 1

    # 3. Bob clicks like again -> liked: False, likes_count: 0 (toggle unlike)
    resp_unlike = client.post(f"/api/v1/posts/{post.id}/like", headers=bob_headers)
    assert resp_unlike.status_code == 200
    data_unlike = resp_unlike.json()
    assert data_unlike["liked"] is False
    assert data_unlike["likes_count"] == 0


def test_comment_flow(client, db_session, test_users, alice_headers, bob_headers):
    post = Post(
        title="Post for Commenting",
        slug="post-for-commenting",
        content="Content for comment testing.",
        is_published=True,
        author_id=test_users["alice"].id
    )
    db_session.add(post)
    db_session.commit()

    # 1. Unauthenticated comment attempt -> 401
    resp_unauth = client.post(
        f"/api/v1/posts/{post.id}/comments",
        json={"content": "Anonymous comment"}
    )
    assert resp_unauth.status_code == 401

    # 2. Bob posts comment -> 201 Created
    resp_comment = client.post(
        f"/api/v1/posts/{post.id}/comments",
        headers=bob_headers,
        json={"content": "Great article, Alice!"}
    )
    assert resp_comment.status_code == 201
    comment_data = resp_comment.json()
    assert comment_data["content"] == "Great article, Alice!"
    assert comment_data["author"]["username"] == "bob"
    comment_id = comment_data["id"]

    # 3. Public visitor can read comments
    resp_list = client.get(f"/api/v1/posts/{post.id}/comments")
    assert resp_list.status_code == 200
    assert len(resp_list.json()) == 1

    # 4. Bob can delete his own comment
    resp_delete = client.delete(f"/api/v1/comments/{comment_id}", headers=bob_headers)
    assert resp_delete.status_code == 200

    # 5. List comments now returns empty
    resp_after = client.get(f"/api/v1/posts/{post.id}/comments")
    assert len(resp_after.json()) == 0


def test_user_cannot_delete_other_users_comment(client, db_session, test_users, alice_headers, bob_headers):
    from app.models.comment import Comment
    post = Post(
        title="Post by Charlie",
        slug="post-by-charlie",
        content="Content by a third party.",
        is_published=True,
        author_id=test_users["alice"].id  # Alice owns post
    )
    db_session.add(post)
    db_session.commit()

    # Alice creates a comment
    comment = Comment(
        content="Comment by Alice",
        post_id=post.id,
        author_id=test_users["alice"].id
    )
    db_session.add(comment)
    db_session.commit()

    # Bob tries to delete Alice's comment
    resp_bob_delete = client.delete(f"/api/v1/comments/{comment.id}", headers=bob_headers)
    assert resp_bob_delete.status_code == 403
