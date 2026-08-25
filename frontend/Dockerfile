FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci --legacy-peer-deps || npm install --legacy-peer-deps

COPY . .

RUN npm run build

EXPOSE 4443

CMD ["node", "build/index.js"]