#!/bin/sh

mc admin user add blog "$BLOG_USER" "$BLOG_PASSWORD"

mc admin policy create blog article-write ../policy/article-policy.json
mc admin policy attach blog article-write --user "$BLOG_USER"
