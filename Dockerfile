FROM ubuntu:14.04

RUN apt-get update
RUN apt-get install -y git-core ruby2.0 ruby2.0-dev
RUN curl -L https://www.chef.io/chef/install.sh | sudo bash
