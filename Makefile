PYTHONDIR := ~/anaconda3/bin

BASIC-PACKAGES:
	sudo apt-get -y install curl

MONGODB:
	sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
	echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | sudo tee /etc/apt/sources.list.d/mongodb.list
	sudo apt-get update
	sudo apt-get -y install mongodb-10gen

RabbitMQ:
	sudo apt-get -y install rabbitmq-server

AnacondaInstall:
	curl --output /tmp/anaconda.sh https://repo.continuum.io/archive/Anaconda3-4.2.0-Linux-x86_64.sh
	/bin/bash /tmp/anaconda.sh
	. ~/.bashrc
	rm /tmp/anaconda.sh

Anaconda:
	@if [ ! -d ~/anaconda3 ] ; \
	then \
		 $(MAKE) AnacondaInstall; \
	fi;

PYTHON3-PACKAGES:
	sudo $(PYTHONDIR)/pip install celery pymongo twitter

JAVA:
	sudo apt-get -y install software-properties-common
	sudo add-apt-repository ppa:webupd8team/java
	sudo apt-get update
	sudo apt-get -y install oracle-java8-installer
	grep -q -F 'export JAVA_HOME="/usr/lib/jvm/java-8-oracle"' ~/.bashrc || echo 'export JAVA_HOME="/usr/lib/jvm/java-8-oracle"' >> ~/.bashrc
	. ~/.bashrc

SPARK: JAVA
	curl http://d3kbcqa49mib13.cloudfront.net/spark-2.0.2-bin-hadoop2.7.tgz | tar xvz -C spark-source --strip-components=1
	grep -q -F 'alias pyspark="PYSPARK_PYTHON=python3 $(shell pwd)/spark-source/bin/pyspark"' ~/.bash_aliases || echo 'alias pyspark="PYSPARK_PYTHON=python3 $(shell pwd)/spark-source/bin/pyspark"' >> ~/.bash_aliases
	grep -q -F 'alias spark_submit="PYSPARK_PYTHON=python3 $(shell pwd)/spark-source/bin/spark-submit"' ~/.bash_aliases || echo 'alias spark_submit="PYSPARK_PYTHON=python3 $(shell pwd)/spark-source/bin/spark-submit"' >> ~/.bash_aliases
	. ~/.bash_aliases

setup:
	sudo apt-get update
	$(MAKE) BASIC-PACKAGES
	$(MAKE) MONGODB
	$(MAKE) RabbitMQ
	$(MAKE) Anaconda
	$(MAKE) PYTHON3-PACKAGES
	$(MAKE) SPARK

develop:
	sudo $(PYTHONDIR)/python3 setup.py --verbose develop

undevelop:
	sudo $(PYTHONDIR)/python3 setup.py --verbose develop --uninstall

dist:
	sudo $(PYTHONDIR)/python3 setup.py sdist -d /tmp/
