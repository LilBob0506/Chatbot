FROM node:20

# Set working directory
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy app code
COPY . .

# Expose default Vite/React dev port
EXPOSE 3000

# Run development server
CMD ["npm", "run", "dev"]
