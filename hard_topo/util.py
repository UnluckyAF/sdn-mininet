"Utility functions for Mininet."

import codecs
import sys

Python3 = sys.version_info[0] == 3
Encoding = 'utf-8' if Python3 else None
class NullCodec( object ):
    "Null codec for Python 2"
    @staticmethod
    def decode( buf ):
        "Null decode"
        return buf

    @staticmethod
    def encode( buf ):
        "Null encode"
        return buf


if Python3:
    def decode( buf ):
        "Decode buffer for Python 3"
        return buf.decode( Encoding )

    def encode( buf ):
        "Encode buffer for Python 3"
        return buf.encode( Encoding )
    getincrementaldecoder = codecs.getincrementaldecoder( Encoding )
else:
    decode, encode = NullCodec.decode, NullCodec.encode
    
    def getincrementaldecoder():
        return NullCodec

