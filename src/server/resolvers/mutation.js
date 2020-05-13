"use strict";
const { createWriteStream, unlink } = require("fs");
const jwt = require("jsonwebtoken");
const bcrypt = require("bcryptjs");
const shortid = require("shortid");

const UPLOAD_DIR = "../media";
module.exports = {
  uploadMedia: async (
    _,
    { media, title, location, year, description, category },
    { dataSources: { mediaDB }, userId }
  ) => {
    if (!userId) {
      throw new Error("Login required");
    }
    const { createReadStream, filename, mimetype } = await media;
    let type = "";
    if (mimetype.includes("image")) {
      type = "PHOTO";
    } else if (mimetype.includes("video")) {
      type = "VIDEO";
    } else {
      throw new Error("Unsupported mimetype");
    }
    const stream = createReadStream();
    const id = shortid.generate();
    const path = `${__dirname}/${UPLOAD_DIR}/original/${id}-${filename}`;
    const originalUrl = `${process.env.URL}:8080/media/original/${id}-${filename}`;

    await new Promise((resolve, reject) => {
      const writeStream = createWriteStream(path);

      writeStream.on("finish", resolve);

      writeStream.on("error", (error) => {
        unlink(path, () => {
          reject(error);
        });
      });

      // In node <= 13, errors are not automatically propagated between piped
      // streams. If there is an error receiving the upload, destroy the write
      // stream with the corresponding error.
      stream.on("error", (error) => writeStream.destroy(error));

      stream.pipe(writeStream);
    });
    return mediaDB.createMedia({
      title,
      description,
      year,
      location,
      type,
      category,
      originalUrl: originalUrl,
      thumbnailUrl: originalUrl,
      url: originalUrl,
      authorId: userId,
      isProcessing: true,
    });
    // TODO(yun-kwak): thumbnail 추출
    // TODO(yun-kwak): 품질 향상 서비스 연결
  },
  deleteMedia: async (_, { id }, { userId, dataSources: { mediaDB } }) => {
    const media = await mediaDB.getMedia(id);
    if (!userId) {
      throw new Error("Login required");
    }
    if (!media) {
      throw new Error("Media not found");
    }
    if (userId !== media.authorId) {
      throw new Error("You are not the author of the media");
    }
    await mediaDB.deleteMedia(id);
    return media;
  },
  signUp: async (_, { email, password, name }, { dataSources: { userDB } }) => {
    const hashedPassword = await bcrypt.hash(password, 3);
    const user = await userDB.createUser({
      email,
      password: hashedPassword,
      name,
    });
    const token = jwt.sign({ userId: user.id }, process.env.SECRET);

    return {
      token,
      user,
    };
  },
  signIn: async (_, args, { dataSources: { userDB } }) => {
    const { password, ...user } = await userDB.getUserByEmail(args.email);
    if (!user) {
      throw new Error("No such user found");
    }
    const valid = await bcrypt.compare(args.password, password);
    if (!valid) {
      throw new Error("Invalid password");
    }

    const token = jwt.sign({ userId: user.id }, process.env.SECRET);
    return {
      token,
      user,
    };
  },
  createComment: async (
    _,
    { mediaId, body },
    { userId, dataSources: { commentDB } }
  ) => {
    if (!userId) {
      throw new Error("Login required");
    }
    const comment = await commentDB.createComment({
      authorId: userId,
      mediaId,
      body,
    });

    return comment;
  },
  deleteComment: async (_, { id }, { userId, dataSources: { commentDB } }) => {
    if (!userId) {
      throw new Error("Login required");
    }
    const comment = await commentDB.getComment(id);
    if (userId !== comment.authorId) {
      throw new Error("You are not the author of the comment");
    }
    if ((await commentDB.deleteComment(id)) !== true) {
      throw new Error("Cannot delete the comment");
    }

    // Success
    return comment;
  },
};
