### BUILD THE GRADLE PROJECT

FROM gradle:jdk11 as java-build

ADD --chown=gradle:gradle gradle /home/gradle/project/gradle
ADD --chown=gradle:gradle chadbot/src /home/gradle/project/chadbot/src
COPY --chown=gradle:gradle chatbot/build.gradle /home/gradle/project/chatbot/build.gradle
COPY --chown=gradle:gradle chatbot/gradlew /home/gradle/project/chatbot/gradlew
COPY --chown=gradle:gradle ./build.gradle /home/gradle/project/build.gradle
COPY --chown=gradle:gradle ./gradlew /home/gradle/project/gradlew
COPY --chown=gradle:gradle ./settings.gradle /home/gradle/project/settings.gradle

WORKDIR /home/gradle/project
# Create a non root user
RUN ./gradlew build -x test adduser --system --home /var/cache/bootapp --shell /sbin/nologin bootapp;

### BUILD THE DOCKER IMAGE
FROM openjdk:11-jre-slim

EXPOSE 8080

# Add jar file to run
COPY --from=java-build /home/gradle/project/chatbot/build/libs/chatbot-1.0-SNAPSHOT.jar /app/chadbot.jar
# Add bootapp user
COPY --from=java-build /etc/passwd /etc/shadow /etc/

WORKDIR /app

# Run as non root (bootapp) user
USER bootapp

ENTRYPOINT ["java","-jar","chadbot.jar"]