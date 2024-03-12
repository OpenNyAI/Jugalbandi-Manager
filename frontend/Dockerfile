FROM node:21-bookworm as builder

WORKDIR /app/frontend

COPY ./frontend/package.json ./frontend/package-lock.json ./

RUN npm install 

COPY ./frontend .

ARG VITE_SERVER_HOST
ENV VITE_SERVER_HOST=${VITE_SERVER_HOST}

RUN npm run build

FROM node:21-bookworm as runtime

WORKDIR /app/frontend

RUN npm install -g serve

COPY --from=builder /app/frontend/dist ./dist

CMD ["serve", "-s", "dist", "-p", "4173"]

