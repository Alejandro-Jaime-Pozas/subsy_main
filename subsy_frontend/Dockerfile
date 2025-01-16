# Use the official Node.js image as the base image
FROM node:16-alpine

# Set the working directory
WORKDIR /subsy_frontend

ENV PATH /subsy_frontend/node_modules/.bin:$PATH

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose the port.
EXPOSE 3000

# Run the application.
CMD [“npm”, “start”]
