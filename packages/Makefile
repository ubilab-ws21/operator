.PHONY: build, publish

ifndef VERSION 
$(error Please use 'make VERSION=x.x-x (LOCAL=true)')
endif
SOURCE_DIR = ue-operator_skeleton
TMP_DIR = ue-operator

all:

ifeq ($(LOCAL),true)
all: build
else
all: build publish
endif

build:
    # creating work directory
	cp -r $(SOURCE_DIR) $(TMP_DIR)
	# copying the webinterface
	mkdir -p $(TMP_DIR)/var/www/html/
	cp -r ../webinterface/* $(TMP_DIR)/var/www/html/
	cp ../MQTTTopics.md $(TMP_DIR)/var/www/html/
	cat ../MQTTTopics.md | cut -d"|" -f4 | grep "/" | sed -e 's/^ /"/g' -e 's/ *$$/",/g' -e '1s/^/let topicList = [\n/g' -e '$$ a ];' > $(TMP_DIR)/var/www/html/topics.js
	# copying the game logic
	mkdir -p $(TMP_DIR)/opt/ue-operator/logic
	cp -r ../logic/* $(TMP_DIR)/opt/ue-operator/logic
	# copying binaries
	mkdir -p $(TMP_DIR)/usr/bin/
	cp -r ../bin/* $(TMP_DIR)/usr/bin/
	# changing directory and binary execution permissions
	sudo chown -R root:root $(TMP_DIR)/etc
	sudo chown -R root:root $(TMP_DIR)/usr
	sudo chown -R root:root $(TMP_DIR)/var
	sudo chmod +x $(TMP_DIR)/usr/bin/ue-operator
	sudo chmod +x $(TMP_DIR)/usr/bin/ue-camera
	sudo chmod +x $(TMP_DIR)/opt/ue-operator/mosquitto_sub
	# Write version and build
	sed -i 's/%VERSION%/$(VERSION)/g' $(TMP_DIR)/DEBIAN/control
	sudo sed -i 's/%VERSION%/$(VERSION)/g' $(TMP_DIR)/usr/bin/ue-operator
	dpkg-deb --build $(TMP_DIR)
	sudo rm -rf $(TMP_DIR)

publish:
	git tag -f -s -m "Version $(VERSION)" v$(VERSION)
	git push origin v$(VERSION) --force
	gpg -ab $(TMP_DIR).deb
	gh release create v$(VERSION) $(TMP_DIR).deb $(TMP_DIR).deb.asc -t "Version $(VERSION)" -n "https://github.com/ubilab-ws21/operator/tree/v$(VERSION)"
	rm $(TMP_DIR).deb $(TMP_DIR).deb.asc
