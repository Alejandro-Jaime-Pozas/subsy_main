# Use the official Node.js image as the base image
FROM node:16-alpine

# Set the working directory
WORKDIR /subsy_frontend

ENV PATH /subsy_frontend/node_modules/.bin:$PATH

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies  # frozen-lockfile ensures consistency, builds exactly what's in package-lock.json
# IF dont have package-lock.json, will need to manually run npm install in local system first to generate
RUN npm install --frozen-lockfile

# Copy the rest of the application code
COPY . .

# Expose the port.
EXPOSE 3000

# Run the application.
CMD ["npm", "start"]
